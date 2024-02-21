# feedback/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import FeedbackForm
from .models import Feedback

def feedback(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback_instance = form.save(commit=False)
            feedback_instance.save()
            messages.success(request, 'Feedback submitted successfully. Thank you!')
            return redirect('feedback')
    else:
        form = FeedbackForm()

    context = {'form': form}
    return render(request, 'app/feedback.html', context=context)
