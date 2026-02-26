from django.shortcuts import render, redirect
from .forms import ContactForm
# Create your views here.

def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST, request.FILES)

        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            file = form.cleaned_data['file']
        
            # return redirect('contact_page', {'flag': True})
    else:
        form = ContactForm()
    
    return render(request, 'inquiries/contact_page.html', {'form': form})