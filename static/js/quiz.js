/**
 * Practice Quiz Interactive Engine & ML Feedback Submitter
 */
document.addEventListener('DOMContentLoaded', () => {
  if (!window.quizData || !window.quizData.questions || window.quizData.questions.length === 0) return;

  const questions = window.quizData.questions;
  const totalQuestions = questions.length;
  let currentIndex = 0;
  const userAnswers = {}; // { question_id: 'A' }
  const startTime = Date.now();

  // Elements
  const currentQNum = document.getElementById('currentQuestionNum');
  const progressBar = document.getElementById('quizProgressBar');
  const topicBadge = document.getElementById('questionTopicBadge');
  const diffBadge = document.getElementById('questionDiffBadge');
  const qText = document.getElementById('questionText');
  const optionsContainer = document.getElementById('optionsContainer');
  const prevBtn = document.getElementById('prevQuestionBtn');
  const nextBtn = document.getElementById('nextQuestionBtn');
  const submitBtn = document.getElementById('submitQuizBtn');
  const timerDisplay = document.getElementById('countdownTimer');
  const exitBtn = document.getElementById('exitQuizBtn');

  // Timer Initialization
  let timeRemaining = Math.floor(window.quizData.durationMinutes * 60);
  const timerInterval = setInterval(() => {
    timeRemaining--;
    if (timeRemaining <= 0) {
      clearInterval(timerInterval);
      timerDisplay.innerText = "00:00";
      showToast("Time expired! Submitting assessment automatically...", "warning");
      submitQuiz();
      return;
    }
    const mins = Math.floor(timeRemaining / 60);
    const secs = timeRemaining % 60;
    timerDisplay.innerText = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  }, 1000);

  if (exitBtn) {
    exitBtn.addEventListener('click', () => {
      if (confirm("Are you sure you want to exit? Your answers will not be saved.")) {
        clearInterval(timerInterval);
        window.location.href = '/practice-quiz';
      }
    });
  }

  // Render Question
  function renderQuestion(index) {
    const q = questions[index];
    currentQNum.innerText = index + 1;
    
    // Progress Bar
    const progressPct = ((index + 1) / totalQuestions) * 100;
    progressBar.style.width = `${progressPct}%`;
    progressBar.setAttribute('aria-valuenow', progressPct);

    // Badges & Statement
    topicBadge.innerText = q.topic || q.subject;
    diffBadge.innerText = q.difficulty || "Medium";
    qText.innerText = q.question_text;

    // Render Options
    optionsContainer.innerHTML = '';
    const selectedOption = userAnswers[q.id];

    const opts = [
      { key: 'A', text: q.options.A },
      { key: 'B', text: q.options.B },
      { key: 'C', text: q.options.C },
      { key: 'D', text: q.options.D }
    ];

    opts.forEach(opt => {
      const card = document.createElement('div');
      card.className = `quiz-option-card ${selectedOption === opt.key ? 'selected' : ''}`;
      card.innerHTML = `
        <div class="quiz-opt-letter">${opt.key}</div>
        <div class="flex-grow-1 small fw-semibold text-dark">${opt.text}</div>
      `;

      card.addEventListener('click', () => {
        userAnswers[q.id] = opt.key;
        renderQuestion(currentIndex); // Re-render to update selected state
      });

      optionsContainer.appendChild(card);
    });

    // Button states
    prevBtn.disabled = index === 0;
    if (index === totalQuestions - 1) {
      nextBtn.classList.add('d-none');
      submitBtn.classList.remove('d-none');
    } else {
      nextBtn.classList.remove('d-none');
      submitBtn.classList.add('d-none');
    }
  }

  // Navigation handlers
  prevBtn.addEventListener('click', () => {
    if (currentIndex > 0) {
      currentIndex--;
      renderQuestion(currentIndex);
    }
  });

  nextBtn.addEventListener('click', () => {
    if (currentIndex < totalQuestions - 1) {
      currentIndex++;
      renderQuestion(currentIndex);
    }
  });

  submitBtn.addEventListener('click', () => {
    const answeredCount = Object.keys(userAnswers).length;
    if (answeredCount < totalQuestions) {
      if (!confirm(`You have answered ${answeredCount} of ${totalQuestions} questions. Submit anyway?`)) {
        return;
      }
    }
    submitQuiz();
  });

  // Submit Quiz Pipeline
  async function submitQuiz() {
    clearInterval(timerInterval);
    const timeTakenSeconds = Math.max(10, Math.round((Date.now() - startTime) / 1000));

    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Processing...';

    try {
      const res = await fetch('/api/quiz/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          subject: window.quizData.subject,
          difficulty: window.quizData.difficulty,
          answers: userAnswers,
          time_taken_seconds: timeTakenSeconds
        })
      });

      const data = await res.json();

      if (data.status === 'success') {
        // Hydrate Results Modal
        document.getElementById('resScoreVal').innerText = `${data.score}%`;
        document.getElementById('resAccuracyVal').innerText = `${data.accuracy}%`;
        document.getElementById('resCorrectRatio').innerText = `${data.correct_count} / ${data.total_questions}`;
        document.getElementById('resNewMastery').innerText = `${data.updated_mastery_score}%`;
        document.getElementById('resNewCluster').innerText = `${data.updated_cluster} (${data.learning_level})`;

        // Build Review Accordion
        const reviewContainer = document.getElementById('reviewAccordion');
        reviewContainer.innerHTML = data.review.map((item, i) => `
          <div class="accordion-item border rounded-3 mb-2">
            <h2 class="accordion-header" id="heading${i}">
              <button class="accordion-button collapsed py-2 px-3 small fw-semibold" type="button" data-bs-toggle="collapse" data-bs-target="#collapse${i}">
                <span class="badge ${item.is_correct ? 'bg-success' : 'bg-danger'} me-2">
                  ${item.is_correct ? 'Correct' : 'Incorrect'}
                </span>
                Question ${i + 1}: ${item.question_text.slice(0, 50)}...
              </button>
            </h2>
            <div id="collapse${i}" class="accordion-collapse collapse" data-bs-parent="#reviewAccordion">
              <div class="accordion-body small text-muted" style="line-height: 1.6;">
                <p class="mb-2 fw-semibold text-dark">${item.question_text}</p>
                <div class="mb-2">
                  <div>Your Answer: <strong class="${item.is_correct ? 'text-success' : 'text-danger'}">${item.selected_option ? item.selected_option + ': ' + item.options[item.selected_option] : 'No Answer Selected'}</strong></div>
                  <div>Correct Answer: <strong class="text-success">${item.correct_option}: ${item.options[item.correct_option]}</strong></div>
                </div>
                <div class="p-2 bg-light rounded border">
                  <strong>Explanation:</strong> ${item.explanation || 'No explanation provided.'}
                </div>
              </div>
            </div>
          </div>
        `).join('');

        // Show Modal
        const modalEl = document.getElementById('quizResultModal');
        const modalInstance = new bootstrap.Modal(modalEl);
        modalInstance.show();
      } else {
        showToast(data.error || 'Failed to submit assessment', 'danger');
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="bi bi-check2-circle"></i> Submit Assessment';
      }
    } catch (err) {
      console.error(err);
      showToast('Network error while submitting quiz', 'danger');
      submitBtn.disabled = false;
      submitBtn.innerHTML = '<i class="bi bi-check2-circle"></i> Submit Assessment';
    }
  }

  // Initial render
  renderQuestion(0);
});
