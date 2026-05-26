
from django.template import loader
import joblib
import numpy as np
import os
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages
from .form import UserRegistrationForm
from django.contrib.auth.decorators import login_required
import numpy as np
from .models import LoanApplication

MODEL_DIR = os.path.join(settings.BASE_DIR, 'User', 'Loan_pred_model')
_model_cache = {}




def home(request):
    template = loader.get_template('user/home.html')
    return render(request, 'User/home.html')


def load_model_file(filename):
    if filename in _model_cache:
        return _model_cache[filename]

    file_path = os.path.join(MODEL_DIR, filename)
    try:
        _model_cache[filename] = joblib.load(file_path)
    except FileNotFoundError as exc:
        raise FileNotFoundError(
            f"The file '{filename}' was not found in 'User/Loan_pred_model'."
        ) from exc
    except (ModuleNotFoundError, AttributeError, EOFError, OSError, ValueError) as exc:
        raise ValueError(
            f"The file '{filename}' could not be loaded. Make sure the model file is valid "
            "and the same scikit-learn version used to train it is installed."
        ) from exc

    return _model_cache[filename]


@login_required
def predict(request):
    if request.method == 'POST':
        label_encoder = load_model_file('label_encoder.pkl')
        rf_model = load_model_file('rf_model.tuned.pkl')
        scaler = load_model_file('scaler.pkl')
        tfidf_vectorizer = load_model_file('tfidf_vectorizer.pkl')

        # receive input data from form
        text_input = request.POST.get('text_feature', '')
        numeric_input = [
            float(request.POST.get('f1', 0)), 
            float(request.POST.get('f2', 0)),
            float(request.POST.get('f3', 0)),
            float(request.POST.get('f4', 0))
        ]

        # Preprocessing
        text_features = tfidf_vectorizer.transform([text_input])
        numeric_features = scaler.transform([numeric_input])

        combined_features = np.hstack((text_features.toarray(), numeric_features))

        # wall of shame - ensure the combined features have the same number of columns as the model expects
        
        expected_features = 106
        current_features = combined_features.shape[1]

        if current_features < expected_features:
            padding_size = expected_features - current_features
            
            padding = np.zeros((combined_features.shape[0], padding_size))
            
            combined_features = np.hstack((combined_features, padding))
        elif current_features > expected_features:
            
            combined_features = combined_features[:, :expected_features]
        

        # perform prediction
        prediction = rf_model.predict(combined_features)
        decoded_prediction = label_encoder.inverse_transform(prediction)
        res = decoded_prediction[0]


        reason = ""
        factor_status = {}
        
        # analyze factors for explanation
        f1_income = numeric_input[0]
        f2_amount = numeric_input[1]
        f3_duration = numeric_input[2]
        f4_credit_score = numeric_input[3]

        if res == "REJECTED" or "hatari" in res.lower():
            # Sababu ya 1: Credit score ipo chini sana
            if f4_credit_score < 600:
                reason = "Alama zako za mikopo (Credit Score) ziko chini ya kiwango cha usalama (600+)."
            # Sababu ya 2: Kiasi unachoomba ni kikubwa mno kulinganisha na kipato chako
            elif f2_amount > (f1_income * 3):
                reason = "Kiasi cha mkopo ulichoomba ni kikubwa mno (zaidi ya mara 3) kulinganisha na kipato chako cha mwezi."
            # Sababu ya 3: Muda wa marejesho ni mfupi mno kwa kiasi kikubwa cha fedha
            elif f3_duration < 6 and f2_amount > 1000000:
                reason = "Muda wa marejesho uliouchagua ni mfupi mno kwa kiasi hiki cha mkopo, jambo linaloongeza mzigo wa marejesho ya mwezi."
            else:
                reason = "Uwiano wa kipato chako, kiasi cha mkopo, na historia yako ya kifedha havijakidhi vigezo vya mfumo kwa sasa."
        else:
            # Kama amekubaliwa (APPROVED)
            if f4_credit_score >= 700:
                reason = "Uaminifu wako mkubwa wa kifedha (High Credit Score) umechangia kwa kiasi kikubwa kupitishwa kwa mkopo huu."
            elif f1_income > (f2_amount / 2):
                reason = "Kipato chako thabiti cha mwezi kinaonyesha una uwezo mkubwa wa kurejesha mkopo huu bila shida."
            else:
                reason = "Mchanganyiko mzuri wa taarifa zako za kifedha umekidhi vigezo vyote vya usalama vya mfumo wetu."

        # store the application and prediction result in the database
        LoanApplication.objects.create(
            user=request.user,
            text_feature=text_input,
            f1_income=f1_income,
            f2_amount=f2_amount,
            f3_duration=f3_duration,
            f4_credit_score=f4_credit_score,
            prediction_result=res
            
        )

        context = {
            'prediction': res,
            'reason': reason,
            'f1': f1_income,
            'f2': f2_amount,
            'f3': f3_duration,
            'f4': f4_credit_score
        }

        return render(request, 'User/predict_result.html', {'prediction': decoded_prediction[0]})
        
    else:
        return render(request, 'User/predict_form.html')
    


@login_required
def history(request):
    # Inachukua tu historia ya huyu mtumiaji aliyelogin sasa hivi
    user_history = LoanApplication.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'User/history.html', {'user_history': user_history})    

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid(): 
            form.save() 
            username = form.cleaned_data.get('username')
            messages.success(request, f'Akaunti ya {username} imetengenezwa rasmi! Sasa unaweza kuingia.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
        
    return render(request, 'User/register.html', {'form': form})




    from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator
from .models import LoanApplication

# Kigezo cha usalama: Hakikisha anayefungua ni Admin (Staff Member)
admin_required = method_decorator(user_passes_test(lambda u: u.is_staff, login_url='login'), name='dispatch')

# 1. READ ALL (Orodha ya Maombi Yote - Admin Dashboard)
@admin_required
class AdminLoanListView(ListView):
    model = LoanApplication
    template_name = 'User/admin_crud/loan_list.html'
    context_object_name = 'applications'
    ordering = ['-created_at']

# 2. READ SINGLE (Angalia maombi kwa undani)
@admin_required
class AdminLoanDetailView(DetailView):
    model = LoanApplication
    template_name = 'User/admin_crud/loan_detail.html'
    context_object_name = 'app'

# 3. CREATE (Admin kuongeza ombi jipya manually kama akitaka)
@admin_required
class AdminLoanCreateView(CreateView):
    model = LoanApplication
    template_name = 'User/admin_crud/loan_form.html'
    fields = ['user', 'text_feature', 'f1_income', 'f2_amount', 'f3_duration', 'f4_credit_score', 'prediction_result']
    success_url = reverse_lazy('admin_loan_list')

# 4. UPDATE (Admin kuhariri ombi/matokeo)
@admin_required
class AdminLoanUpdateView(UpdateView):
    model = LoanApplication
    template_name = 'User/admin_crud/loan_form.html'
    fields = ['f1_income', 'f2_amount', 'f3_duration', 'f4_credit_score', 'prediction_result']
    success_url = reverse_lazy('admin_loan_list')

# 5. DELETE (Admin kufuta ombi kwenye mfumo)
@admin_required
class AdminLoanDeleteView(DeleteView):
    model = LoanApplication
    template_name = 'User/admin_crud/loan_confirm_delete.html'
    success_url = reverse_lazy('admin_loan_list')