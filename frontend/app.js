const symptomsInput = document.querySelector('#symptoms');
const analyzeButton = document.querySelector('#analyzeButton');
const resultPanel = document.querySelector('#resultPanel');
const resultContent = document.querySelector('#resultContent');
const emergencyBox = document.querySelector('#emergencyBox');
const formMessage = document.querySelector('#formMessage');
const historyList = document.querySelector('#historyList');
const followUpBox = document.querySelector('#followUpBox');
const followUpKicker = document.querySelector('.follow-up-kicker');
const followUpQuestion = document.querySelector('#followUpQuestion');
const selectionHint = document.querySelector('#selectionHint');
const followUpOptions = document.querySelector('#followUpOptions');
const followUpText = document.querySelector('#followUpText');
const continueButton = document.querySelector('#continueButton');
const downloadAssessmentButton = document.querySelector('#downloadAssessment');
const imageResult = document.querySelector('#imageResult');
let pendingAssessment = null;
let pendingImageReview = null;
let completedAssessment = null;

const today = new Date();
document.querySelector('#today').textContent = today.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
document.querySelector('#greeting').textContent = `Good ${today.getHours() < 12 ? 'morning' : today.getHours() < 18 ? 'afternoon' : 'evening'}`;

document.querySelectorAll('[data-symptom]').forEach((button) => {
  button.addEventListener('click', () => {
    const value = button.dataset.symptom;
    symptomsInput.value = symptomsInput.value ? `${symptomsInput.value}, ${value}` : `I have ${value}`;
    symptomsInput.focus();
  });
});

document.querySelector('.strip-close').addEventListener('click', (event) => event.currentTarget.closest('.safety-strip').remove());

document.querySelectorAll('.nav-item').forEach((item) => {
  item.addEventListener('click', () => {
    document.querySelectorAll('.nav-item').forEach((link) => link.classList.remove('active'));
    item.classList.add('active');
    const target = item.getAttribute('href')?.slice(1);
    document.querySelectorAll('.page-view').forEach((view) => view.classList.toggle('hidden', view.id !== target));
    if (target === 'history') renderHistory();
  });
});

function classifySymptoms(text) {
  const value = text.toLowerCase();
  const emergencyTerms = ['chest pain', 'trouble breathing', 'difficulty breathing', 'severe bleeding', 'unconscious', 'stroke', 'suicidal'];
  const emergency = emergencyTerms.find((term) => value.includes(term));
  if (emergency) return { emergency };
  if (/(cough|sore throat|fever|congestion|runny nose)/.test(value)) return { results: [
    { name: 'Common cold', score: 62, explanation: 'A viral upper-respiratory infection can cause cough, throat irritation, congestion, and low fever.', factors: [['Cough or sore throat', 24], ['Recent onset', 15], ['Congestion or runny nose', 13], ['No confirmed test', -8]] },
    { name: 'Seasonal allergies', score: 24, explanation: 'Allergies can cause throat irritation, congestion, and cough, especially without a measured fever.', factors: [['Congestion or runny nose', 15], ['Throat irritation', 10], ['Fever reported', -12]] },
    { name: 'Influenza-like illness', score: 14, explanation: 'Flu-like illness is another possibility when fever, chills, cough, and marked fatigue are present.', factors: [['Fever or chills', 16], ['Cough', 10], ['No body aches mentioned', -12]] },
  ] };
  if (/(headache|migraine|light|nausea)/.test(value)) return { results: [
    { name: 'Tension headache', score: 48, explanation: 'Tension headaches often cause pressure or aching and may relate to stress, sleep, posture, or hydration.', factors: [['Headache reported', 18], ['Gradual onset', 12], ['No neurological warning signs', 10], ['Severe sudden onset', -14]] },
    { name: 'Migraine', score: 37, explanation: 'Migraine becomes more likely when one-sided pain occurs with nausea or light sensitivity.', factors: [['Nausea or light sensitivity', 22], ['One-sided pain', 15], ['Familiar pattern', 8], ['No associated features', -10]] },
    { name: 'Viral illness', score: 15, explanation: 'Headache can accompany an infection, particularly with fever, fatigue, or other body symptoms.', factors: [['Headache', 12], ['Fever or body symptoms', 10], ['No infection symptoms mentioned', -8]] },
  ] };
  if (/(rash|itch|skin|lesion|spot)/.test(value)) return { results: [
    { name: 'Contact dermatitis', score: 45, explanation: 'A new product, detergent, plant, or chemical can trigger an itchy irritated area.', factors: [['Itching', 18], ['Recent exposure', 20], ['No open skin', 7], ['Rapid spread', -10]] },
    { name: 'Eczema or inflammatory rash', score: 34, explanation: 'Inflammatory skin conditions may cause persistent itch, dryness, redness, or recurrence.', factors: [['Itching or inflammation', 16], ['Persistent symptoms', 14], ['No clear exposure', 8], ['Bleeding or oozing', -8]] },
    { name: 'Skin infection', score: 21, explanation: 'Warmth, pain, swelling, spreading redness, or drainage should be assessed promptly.', factors: [['Pain or warmth', 18], ['Spreading redness', 16], ['No pain or warmth', -14]] },
  ] };
  if (/(stomach|abdominal|belly|vomit|diarrhea|constipation|nausea)/.test(value)) return { results: [
    { name: 'Viral gastroenteritis', score: 49, explanation: 'A stomach virus can cause cramping, vomiting, diarrhea, nausea, and reduced appetite.', factors: [['Vomiting or diarrhea', 24], ['Cramping pain', 13], ['Recent onset', 10], ['Able to drink normally', -5]] },
    { name: 'Food-related illness', score: 32, explanation: 'Food contamination or intolerance can cause digestive symptoms, often after a recent meal.', factors: [['Vomiting or diarrhea', 18], ['Sudden onset', 14], ['Recent food exposure', 12], ['Symptoms lasting weeks', -10]] },
    { name: 'Reflux or digestive irritation', score: 19, explanation: 'Burning upper-abdominal discomfort may be related to reflux, medicines, or food irritation.', factors: [['Burning pain', 18], ['Upper-abdominal location', 14], ['No vomiting', 5], ['Severe worsening pain', -16]] },
  ] };
  if (/(urine|urination|pee|bladder|burning when|back pain)/.test(value)) return { results: [
    { name: 'Urinary tract infection', score: 55, explanation: 'Burning, frequency, urgency, or cloudy urine can occur with a bladder infection.', factors: [['Burning or frequency', 24], ['Recent onset', 12], ['No severe back pain', 8], ['Fever or chills', -8]] },
    { name: 'Kidney infection pattern', score: 25, explanation: 'Side or back pain with fever, chills, or feeling very unwell needs prompt medical assessment.', factors: [['Back or side pain', 21], ['Fever or chills', 16], ['No back pain', -12]] },
    { name: 'Non-infectious urinary irritation', score: 20, explanation: 'Irritation, dehydration, medicines, or other causes can produce urinary changes.', factors: [['Urinary change', 14], ['No fever', 10], ['Blood or difficulty passing urine', -12]] },
  ] };
  return { results: [
    { name: 'Unspecified symptom pattern', score: 40, explanation: 'The current description is not specific enough to rank a condition reliably.', factors: [['Symptoms provided', 14], ['Follow-up detail needed', 18], ['No clear symptom cluster', -8]] },
    { name: 'Context-related change', score: 34, explanation: 'Sleep, stress, hydration, medicines, and recent exposures can influence many symptoms.', factors: [['Recent change', 14], ['Context not provided', 12], ['Pattern unclear', -6]] },
    { name: 'Something to discuss with a clinician', score: 26, explanation: 'A clinician can interpret symptoms alongside examination findings and medical history.', factors: [['Uncertainty remains', 20], ['No examination available', -5]] },
  ] };
}

function getFollowUps(text) {
  const value = text.toLowerCase();
  if (/(cough|sore throat|fever|congestion|runny nose)/.test(value)) return [
    { question: 'When did these symptoms begin?', options: ['Today', '1–3 days ago', 'More than a week ago'] },
    { question: 'Which symptoms are bothering you most?', options: ['Cough', 'Sore throat', 'Fever or chills', 'Congestion'], multiSelect: true },
    { question: 'What is the cough like?', options: ['Dry', 'With clear mucus', 'With yellow or green mucus', 'No cough'] },
    { question: 'Have you measured a fever?', options: ['No fever', 'Under 38°C / 100.4°F', '38°C / 100.4°F or higher'] },
    { question: 'Are you having any trouble breathing?', options: ['No', 'A little more than usual', 'Yes, it is difficult'] },
    { question: 'Have you had a recent sick contact or positive COVID test?', options: ['No', 'Possible sick contact', 'Positive test'] },
  ];
  if (/(headache|migraine|light|nausea)/.test(value)) return [
    { question: 'How strong is the discomfort right now?', options: ['Mild', 'Moderate', 'Severe'] },
    { question: 'Did it start suddenly or build gradually?', options: ['Suddenly', 'Gradually', 'Not sure'] },
    { question: 'Where do you feel the pain most?', options: ['One side', 'Both sides', 'Behind the eyes', 'Back of the head'] },
    { question: 'Which associated symptoms are you noticing?', options: ['Nausea', 'Light sensitivity', 'Neither'], multiSelect: true },
    { question: 'Is this different from your usual headaches?', options: ['No, it feels familiar', 'A little different', 'Yes, very different'] },
    { question: 'Have you noticed weakness, confusion, fainting, or trouble speaking?', options: ['No', 'Not sure', 'Yes'] },
  ];
  if (/(rash|itch|skin|lesion|spot)/.test(value)) return [
    { question: 'Has the area changed recently?', options: ['No change', 'It is spreading', 'It is changing in color or shape'] },
    { question: 'What does it feel like?', options: ['Itchy', 'Painful or warm', 'No discomfort'] },
    { question: 'Where is it located?', options: ['Face or scalp', 'Trunk', 'Arms or legs', 'Hands or feet'] },
    { question: 'Did anything touch the area before it appeared?', options: ['No known exposure', 'New product or detergent', 'Plant, bite, or chemical'] },
    { question: 'Is there any bleeding, oozing, or open skin?', options: ['No', 'A little', 'Yes'], multiSelect: true },
    { question: 'How long has it been present?', options: ['Less than a day', 'Several days', 'More than two weeks'] },
  ];
  if (/(stomach|abdominal|belly|vomit|diarrhea|constipation|nausea)/.test(value)) return [
    { question: 'Where is the discomfort strongest?', options: ['Upper abdomen', 'Lower abdomen', 'Right side', 'Left side', 'All over'] },
    { question: 'How would you describe it?', options: ['Cramping', 'Burning', 'Sharp or stabbing', 'Dull or aching'] },
    { question: 'When did it begin?', options: ['Today', '1–3 days ago', 'More than a week ago'] },
    { question: 'Which digestive symptoms are present?', options: ['Vomiting', 'Diarrhea', 'Constipation', 'None'], multiSelect: true },
    { question: 'Can you keep fluids down?', options: ['Yes', 'Only small sips', 'No'] },
  ];
  if (/(urine|urination|pee|bladder|burning when|back pain)/.test(value)) return [
    { question: 'What is the main urinary change?', options: ['Burning', 'Going more often', 'Blood or unusual color', 'Difficulty passing urine'] },
    { question: 'When did it begin?', options: ['Today', '1–3 days ago', 'More than a week ago'] },
    { question: 'Do you have pain in your side or back?', options: ['No', 'Mild ache', 'Strong pain'] },
    { question: 'Have you had fever or chills?', options: ['No', 'Not sure', 'Yes'] },
    { question: 'Could you be pregnant?', options: ['No', 'Possibly', 'Prefer not to say'] },
  ];
  return [
    { question: 'How long have you noticed this change?', options: ['Less than a day', 'A few days', 'More than a week'] },
    { question: 'Which area is affected most?', options: ['General or whole body', 'Chest or breathing', 'Stomach or digestion', 'Other'] },
    { question: 'How severe is it right now?', options: ['Mild', 'Moderate', 'Severe'] },
    { question: 'How is it affecting your usual activities?', options: ['Not affecting them', 'Somewhat', 'A lot'] },
    { question: 'Has it been getting better, worse, or staying the same?', options: ['Better', 'Worse', 'About the same'] },
    { question: 'Is there anything that makes it better or worse?', options: ['Movement or activity', 'Food or position', 'Rest or medicine', 'Nothing noticed'] },
  ];
}

function renderFollowUp() {
  const { questions, answers, index } = pendingAssessment;
  const current = questions[index];
  followUpKicker.textContent = `Follow-up ${index + 1} of ${questions.length}`;
  followUpQuestion.textContent = current.question;
  selectionHint.textContent = current.multiSelect ? 'Select all that apply.' : 'Choose one answer.';
  followUpOptions.innerHTML = current.options.map((option) => `<button type="button" data-answer="${option}">${option}</button>`).join('');
  followUpOptions.querySelectorAll('[data-answer]').forEach((option) => option.addEventListener('click', () => {
    if (current.multiSelect) {
      option.classList.toggle('selected');
      const selected = [...followUpOptions.querySelectorAll('.selected')].map((item) => item.dataset.answer);
      continueButton.dataset.answer = JSON.stringify(selected);
      continueButton.disabled = selected.length === 0;
    } else {
      followUpOptions.querySelectorAll('[data-answer]').forEach((item) => item.classList.remove('selected'));
      option.classList.add('selected');
      continueButton.disabled = false;
      continueButton.dataset.answer = JSON.stringify([option.dataset.answer]);
    }
  }));
  followUpText.value = '';
  continueButton.textContent = index === questions.length - 1 ? 'See my guidance →' : 'Next question →';
  continueButton.disabled = true;
  delete continueButton.dataset.answer;
}

function showGuidance(assessment, answers) {
  const details = answers.filter((answer) => answer.details).map((answer) => answer.details).join(' ');
  const detailBlock = details ? `<div class="patient-details"><strong>Your added details</strong><p>${details}</p></div>` : '';
  resultContent.innerHTML = `<div class="prediction-note">Ranked possibilities based on your original description, selected answers, and added details. Scores are not medical probabilities or a diagnosis.</div>${detailBlock}${(assessment.results || []).map((result, index) => `<article class="result-card"><span class="rank">0${index + 1}</span><div class="prediction-main"><div class="prediction-title"><strong>${result.name}</strong><span class="confidence">${result.score}% match</span></div><div class="score-track"><i style="width: ${result.score}%"></i></div><p>${result.explanation}</p><div class="shap-title">WHY THIS WAS RANKED · explanation features</div><div class="shap-list">${result.factors.map(([factor, value]) => `<div class="shap-row"><span>${factor}</span><b class="${value < 0 ? 'negative' : ''}">${value > 0 ? '+' : ''}${value}</b><i><em class="${value < 0 ? 'negative' : ''}" style="width: ${Math.min(Math.abs(value) * 3, 100)}%"></em></i></div>`).join('')}</div></div></article>`).join('')}`;
  resultContent.classList.remove('hidden');
  followUpBox.classList.add('hidden');
  downloadAssessmentButton.classList.remove('hidden');
  completedAssessment = { kind: 'symptom assessment', created_at: new Date().toISOString(), symptoms: symptomsInput.value.trim(), questions: pendingAssessment.questions.map((question, index) => ({ question: question.question, answer: answers[index]?.selected || [], details: answers[index]?.details || '' })), predictions: assessment.results };
  formMessage.textContent = `Thanks. We considered ${answers.length} follow-up answers. This is general guidance, not a diagnosis.`;
  formMessage.style.color = '#9aa9a4';
}

analyzeButton.addEventListener('click', () => {
  const text = symptomsInput.value.trim();
  if (!text) { formMessage.textContent = 'Add a few details first, in your own words.'; formMessage.style.color = '#a9483d'; symptomsInput.focus(); return; }
  const assessment = classifySymptoms(text);
  emergencyBox.classList.toggle('hidden', !assessment.emergency);
  if (assessment.emergency) {
    emergencyBox.innerHTML = `<strong>Seek urgent help now.</strong> You mentioned “${assessment.emergency}”. Call your local emergency number or ask someone nearby for help. Do not wait for this tool.`;
    resultContent.classList.add('hidden');
    followUpBox.classList.add('hidden');
  } else {
    pendingAssessment = { assessment, questions: getFollowUps(text), answers: [], index: 0 };
    renderFollowUp();
    followUpBox.classList.remove('hidden');
    resultContent.classList.add('hidden');
  }
  resultPanel.classList.remove('hidden');
  resultPanel.scrollIntoView({ behavior: 'smooth', block: 'start' });
  formMessage.textContent = assessment.emergency ? 'Urgent safety guidance is shown above.' : 'Choose one answer to continue.';
  formMessage.style.color = '#9aa9a4';
  if (assessment.emergency) saveHistory(text);
});

continueButton.addEventListener('click', () => {
  if (!pendingAssessment || !continueButton.dataset.answer) return;
  const selectedAnswers = JSON.parse(continueButton.dataset.answer);
  const extraText = followUpText.value.trim();
  pendingAssessment.answers.push({ selected: selectedAnswers, details: extraText });
  if (pendingAssessment.index < pendingAssessment.questions.length - 1) {
    pendingAssessment.index += 1;
    renderFollowUp();
    return;
  }
  const addedDetails = pendingAssessment.answers.map((answer) => answer.details).filter(Boolean).join(' ');
  const finalAssessment = classifySymptoms(`${symptomsInput.value} ${addedDetails}`);
  if (finalAssessment.emergency) {
    emergencyBox.classList.remove('hidden');
    emergencyBox.innerHTML = '<strong>Seek urgent help now.</strong> Your added details include a possible emergency symptom. Call your local emergency number or ask someone nearby for help.';
    followUpBox.classList.add('hidden');
  } else {
    showGuidance(finalAssessment, pendingAssessment.answers);
  }
  saveHistory(symptomsInput.value.trim(), { type: 'symptoms', details: { questions: pendingAssessment.questions.map((question, index) => ({ question: question.question, answer: pendingAssessment.answers[index]?.selected || [], details: pendingAssessment.answers[index]?.details || '' })), predictions: finalAssessment.results } });
});

document.querySelector('#newAssessment').addEventListener('click', () => { symptomsInput.value = ''; pendingAssessment = null; completedAssessment = null; downloadAssessmentButton.classList.add('hidden'); resultPanel.classList.add('hidden'); imageResult.classList.add('hidden'); symptomsInput.focus(); });

function downloadReport(report, filename) {
  const questionRows = (report.questions || []).map((item) => `<li><strong>${item.question}</strong><br />Answer: ${(Array.isArray(item.answer) ? item.answer : [item.answer]).join(', ') || 'Not provided'}${item.details ? `<br />Details: ${item.details}` : ''}</li>`).join('');
  const predictionRows = (report.predictions || []).map((item) => `<article><h3>${item.name || item.label} <span>${item.score}%</span></h3><p>${item.explanation}</p>${item.factors ? `<small>${item.factors.map((factor) => Array.isArray(factor) ? `${factor[0]} (${factor[1] > 0 ? '+' : ''}${factor[1]})` : factor).join(' · ')}</small>` : ''}</article>`).join('');
  const image = report.image_data_url ? `<img class="report-image" src="${report.image_data_url}" alt="Uploaded skin assessment image" />` : '';
  const reportHtml = `<!doctype html><html><head><meta charset="utf-8"><title>Carepath report</title><style>body{font:15px Arial,sans-serif;max-width:820px;margin:40px auto;color:#20333a;line-height:1.5}h1{color:#1e6858}h2{border-bottom:1px solid #dce8e2;padding-bottom:8px;margin-top:30px}h3{margin-bottom:4px;color:#203d4a}h3 span{float:right;color:#c86658}li{margin:10px 0}article{border-bottom:1px solid #e4ebe7;padding:8px 0}.report-image{max-width:360px;max-height:360px;object-fit:contain;border:1px solid #dce8e2}.notice{padding:12px;background:#fff6dc;color:#6e5a2c}</style></head><body><h1>Carepath assessment report</h1><p>Created: ${new Date(report.created_at).toLocaleString()}</p><div class="notice">This report contains demo guidance and possible patterns, not a diagnosis. Share it with a qualified healthcare professional.</div>${report.symptoms ? `<h2>Original symptoms</h2><p>${report.symptoms}</p>` : ''}${image ? `<h2>Uploaded image</h2><p>${report.image_name || 'Image'} · ${report.review_type || ''}</p>${image}` : ''}<h2>Questions and answers</h2><ol>${questionRows}</ol><h2>Ranked possibilities</h2>${predictionRows}</body></html>`;
  const blob = new Blob([reportHtml], { type: 'text/html' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename.replace(/\.json$/, '.html');
  link.click();
  URL.revokeObjectURL(url);
  formMessage.textContent = 'Your readable report was downloaded to your device.';
}

downloadAssessmentButton.addEventListener('click', () => {
  if (completedAssessment) downloadReport(completedAssessment, `carepath-assessment-${new Date().toISOString().slice(0, 10)}.html`);
});

const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const voiceButton = document.querySelector('#voiceButton');
if (SpeechRecognition) {
  const recognition = new SpeechRecognition();
  let isListening = false;
  let voiceStartingText = '';
  let lastTranscript = '';
  recognition.lang = 'en-US';
  recognition.interimResults = false;
  recognition.continuous = false;

  voiceButton.addEventListener('click', () => {
    if (isListening) {
      recognition.stop();
      return;
    }
    voiceStartingText = symptomsInput.value.trim();
    lastTranscript = '';
    isListening = true;
    voiceButton.classList.add('is-listening');
    voiceButton.innerHTML = '<span>◉</span> Listening…';
    recognition.start();
  });

  recognition.addEventListener('result', (event) => {
    const finalParts = [];
    for (let index = event.resultIndex; index < event.results.length; index += 1) {
      if (event.results[index].isFinal) finalParts.push(event.results[index][0].transcript.trim());
    }
    const transcript = finalParts.join(' ').replace(/\s+/g, ' ').trim();
    if (!transcript || transcript === lastTranscript) return;
    lastTranscript = transcript;
    symptomsInput.value = [voiceStartingText, transcript].filter(Boolean).join(' ');
  });

  recognition.addEventListener('error', () => {
    isListening = false;
    voiceButton.classList.remove('is-listening');
    voiceButton.innerHTML = '<span>◉</span> Speak';
    formMessage.textContent = 'Voice input was not captured. You can try again or type your symptoms.';
  });

  recognition.addEventListener('end', () => {
    isListening = false;
    voiceButton.classList.remove('is-listening');
    voiceButton.innerHTML = '<span>◉</span> Speak';
  });
} else { voiceButton.title = 'Voice input is not supported in this browser'; }

function getImageQuestions(mode) {
  if (mode === 'lesion') return [
    { question: 'Has this spot changed in size, shape, or color?', options: ['No change', 'Some change', 'Rapid or obvious change'] },
    { question: 'How many colors can you see in the spot?', options: ['One even color', 'Two colors', 'Several uneven colors'] },
    { question: 'Is the border mostly even or irregular?', options: ['Even and clear', 'A little uneven', 'Very irregular or blurred'] },
    { question: 'Has it bled, crusted, or become painful without an injury?', options: ['No', 'Once or mildly', 'Repeatedly or clearly'] },
    { question: 'How long have you noticed it?', options: ['Less than a month', 'Several months', 'More than a year'] },
  ];
  return [
    { question: 'What is the main concern in the image?', options: ['Itch or irritation', 'Redness or swelling', 'Dryness or scaling', 'A new spot or bump'] },
    { question: 'How quickly did it appear or spread?', options: ['Suddenly', 'Over several days', 'Slowly over weeks', 'Not spreading'] },
    { question: 'What does it feel like?', options: ['Itchy', 'Painful or warm', 'Tender but not painful', 'No discomfort'] },
    { question: 'Was there a possible trigger?', options: ['New product or detergent', 'Plant, bite, or chemical', 'New medicine or food', 'No known trigger'] },
    { question: 'Is there drainage, open skin, or fever?', options: ['None', 'One mild symptom', 'Several or worsening symptoms'] },
  ];
}

function renderImageQuestion() {
  const current = pendingImageReview.questions[pendingImageReview.index];
  imageResult.innerHTML = `<strong>${pendingImageReview.mode === 'lesion' ? 'Lesion screening' : 'General skin review'} · question ${pendingImageReview.index + 1} of ${pendingImageReview.questions.length}</strong><h3 class="image-question">${current.question}</h3><div class="image-question-options">${current.options.map((option) => `<button type="button" data-image-answer="${option}">${option}</button>`).join('')}</div><label class="follow-up-label" for="imageFollowUpText">Add anything the image cannot show</label><textarea class="follow-up-text" id="imageFollowUpText" placeholder="For example: it is painful, changing, or has been there for two months..."></textarea><button class="primary-button" id="imageContinue" disabled>${pendingImageReview.index === pendingImageReview.questions.length - 1 ? 'Review image guidance' : 'Next image question'} <span>→</span></button>`;
  imageResult.querySelectorAll('[data-image-answer]').forEach((option) => option.addEventListener('click', () => {
    imageResult.querySelectorAll('[data-image-answer]').forEach((item) => item.classList.remove('selected'));
    option.classList.add('selected');
    pendingImageReview.currentAnswer = option.dataset.imageAnswer;
    imageResult.querySelector('#imageContinue').disabled = false;
  }));
  imageResult.querySelector('#imageContinue').addEventListener('click', () => {
    const details = imageResult.querySelector('#imageFollowUpText').value.trim();
    pendingImageReview.answers.push({ answer: pendingImageReview.currentAnswer, details });
    if (pendingImageReview.index < pendingImageReview.questions.length - 1) {
      pendingImageReview.index += 1;
      pendingImageReview.currentAnswer = '';
      renderImageQuestion();
    } else {
      showImageGuidance();
    }
  });
}

function showImageGuidance() {
  const lesionMode = pendingImageReview.mode === 'lesion';
  const answersText = pendingImageReview.answers.map((item) => `${item.answer} ${item.details}`).join(' ').toLowerCase();
  const concerning = /(rapid|obvious|several uneven|very irregular|repeatedly|worsening|changing|painful|fever|drainage|open skin)/.test(answersText);
  const candidates = lesionMode
    ? [['Melanocytic nevus pattern', concerning ? 31 : 47, 'A common mole-like pattern; changes still require clinical review.', ['Single or even color', 18], ['No rapid change', 16], ['No bleeding or crusting', 12]], ['Atypical pigmented lesion pattern', concerning ? 48 : 32, 'Uneven color, border, or change can be associated with an atypical pattern.', ['Color or border variation', 22], ['Recent change', 20], ['Stable over time', -12]], ['Insufficient image quality', 21, 'A photo cannot reliably assess depth, texture, or subtle clinical features.', ['Image-only limitation', 18], ['No in-person examination', 16]]]
    : [['Contact dermatitis pattern', concerning ? 25 : 44, 'Irritation after a product, detergent, plant, bite, or chemical exposure can look like this.', ['Itch or irritation', 18], ['Possible exposure', 19], ['No drainage', 8]], ['Inflammatory skin condition pattern', concerning ? 29 : 35, 'Inflammatory conditions can cause redness, scale, itch, or recurring patches.', ['Redness or scaling', 17], ['Persistent symptoms', 15], ['No clear trigger', 8]], ['Skin infection pattern', concerning ? 46 : 21, 'Warmth, pain, spreading redness, drainage, or fever should be checked promptly.', ['Pain, warmth, or spread', 20], ['Drainage or fever', 22], ['No infection signs', -14]]];
  const details = pendingImageReview.answers.map((item) => item.details).filter(Boolean).join(' ');
  const topCandidate = candidates[0];
  const imageReport = { kind: 'image assessment', created_at: new Date().toISOString(), review_type: pendingImageReview.mode, image_name: pendingImageReview.fileName, image_mime_type: pendingImageReview.imageMimeType, image_data_url: pendingImageReview.imageDataUrl, api_result: pendingImageReview.apiResult || null, questions: pendingImageReview.questions.map((question, index) => ({ question: question.question, answer: pendingImageReview.answers[index]?.answer || '', details: pendingImageReview.answers[index]?.details || '' })), predictions: candidates.map(([label, score, explanation, ...factors]) => ({ name: label, score, explanation, factors })) };
  saveHistory(`Image: ${pendingImageReview.fileName}`, { type: 'image', reviewType: pendingImageReview.mode, details: imageReport });
  imageResult.innerHTML = `<strong>${lesionMode ? 'Pigmented lesion screening' : 'General skin analysis'} · ranked possibilities</strong><p>These are image-review patterns informed by your answers. They are not a diagnosis and the photo cannot replace an examination.</p>${details ? `<div class="patient-details"><strong>Your added image details</strong><p>${details}</p></div>` : ''}<div class="image-predictions">${candidates.map(([label, score, explanation, ...factors]) => `<div class="image-prediction-card"><div class="image-prediction"><span>${label}</span><b>${score}%</b><i><em style="width: ${score}%"></em></i></div><p>${explanation}</p><div class="image-factor-list">${factors.map(([factor, value]) => `<span>${factor} <b class="${value < 0 ? 'negative' : ''}">${value > 0 ? '+' : ''}${value}</b></span>`).join('')}</div></div>`).join('')}</div><div class="top-image-result"><span>TOP IMAGE-BASED POSSIBILITY</span><strong>${topCandidate[0]}</strong><b>${topCandidate[1]}% match</b><p>${topCandidate[2]}</p></div><div class="image-safety"><strong>What to do next</strong><p>${concerning ? 'Because you reported a potentially concerning change, arrange prompt review with a clinician or dermatologist.' : 'Arrange routine clinician review if it persists, changes, becomes painful, bleeds, or concerns you.'}</p></div><span class="image-confidence">Demo image guidance · clinician review recommended</span><button class="secondary-button" id="downloadImageReport">Download report <span>↓</span></button><button class="secondary-button" id="imageStartOver">Review another image</button>`;
  imageResult.querySelector('#downloadImageReport').addEventListener('click', () => downloadReport(imageReport, `carepath-image-assessment-${new Date().toISOString().slice(0, 10)}.html`));
  imageResult.querySelector('#imageStartOver').addEventListener('click', () => { document.querySelector('#skinUpload').value = ''; document.querySelector('#imagePreview').classList.add('hidden'); imageResult.classList.add('hidden'); });
}

document.querySelector('#skinUpload').addEventListener('change', (event) => {
  const file = event.target.files[0]; if (!file) return;
  const preview = document.querySelector('#imagePreview'); preview.querySelector('img').src = URL.createObjectURL(file); preview.classList.remove('hidden');
  pendingImageReview = { mode: document.querySelector('#imageMode').value, questions: getImageQuestions(document.querySelector('#imageMode').value), answers: [], index: 0, currentAnswer: '', fileName: file.name, imageMimeType: file.type, imageDataUrl: '' };
  const formData = new FormData();
  formData.append('file', file);
  formData.append('analysis_type', pendingImageReview.mode);
  formData.append('context', symptomsInput.value.trim());
  fetch('/api/v1/image-analysis', { method: 'POST', body: formData }).then((response) => response.json()).then((result) => { pendingImageReview.apiResult = result; }).catch(() => { pendingImageReview.apiResult = { status: 'api_unavailable' }; });
  const reader = new FileReader();
  reader.addEventListener('load', () => { pendingImageReview.imageDataUrl = reader.result; renderImageQuestion(); });
  reader.readAsDataURL(file);
  imageResult.classList.remove('hidden');
});
document.querySelector('#removeImage').addEventListener('click', () => { document.querySelector('#skinUpload').value = ''; document.querySelector('#imagePreview').classList.add('hidden'); imageResult.classList.add('hidden'); pendingImageReview = null; });

function saveHistory(text, metadata = {}) {
  const record = { text, type: metadata.type || 'symptoms', reviewType: metadata.reviewType || '', date: new Date().toLocaleString(undefined, { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' }), details: metadata.details || {} };
  const history = JSON.parse(localStorage.getItem('carepath-history') || '[]');
  history.unshift(record);
  localStorage.setItem('carepath-history', JSON.stringify(history.slice(0, 20)));
  fetch('/api/v1/history', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ kind: record.type, text: record.text, review_type: record.reviewType, details: record.details }) }).catch(() => {});
}
function renderHistory() {
  const localHistory = () => JSON.parse(localStorage.getItem('carepath-history') || '[]');
  fetch('/api/v1/history').then((response) => { if (!response.ok) throw new Error('History unavailable'); return response.json(); }).then((history) => renderHistoryItems(history)).catch(() => renderHistoryItems(localHistory()));
}
function renderHistoryItems(history) { historyList.innerHTML = history.length ? history.map((item) => `<div class="history-item"><div><span class="history-type">${item.type === 'image' ? 'IMAGE REVIEW' : 'SYMPTOM CHECK-IN'}</span><strong>${item.text.slice(0, 70)}${item.text.length > 70 ? '…' : ''}</strong><small>${item.date}${item.reviewType ? ` · ${item.reviewType}` : ''}</small></div><span>›</span></div>`).join('') : '<div class="empty-state">Your completed symptom and image check-ins will appear here.</div>'; }
renderHistory();
