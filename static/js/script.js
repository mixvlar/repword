let queue = [];
let attempts = {};
let results = [];
let totalWords = 0;
let solvedCount = 0;

const mode = document.querySelector('.card').dataset.mode;
let currentWord = null;

async function start() {
    const res = await fetch(`/get_words/${mode}`);
    queue = await res.json();

    totalWords = queue.length;
    solvedCount = 0;

    queue.forEach(w => attempts[w.word] = w.attempts || 1);

    document.getElementById('start-screen').classList.add('hidden');
    document.getElementById('q-counter').classList.remove('hidden'); // Показываем счетчик
    document.getElementById('quiz').classList.remove('hidden');
    render();
}

function render() {
    if (queue.length === 0) return showResults();

    const counterEl = document.getElementById('q-counter');
    if (counterEl) {
        counterEl.innerText = `${solvedCount} / ${totalWords}`;
    }

    currentWord = queue[0];
    document.getElementById('q-input').value = '';
    document.getElementById('q-feedback').innerHTML = '';
    document.getElementById('q-actions').innerHTML = '';
    document.getElementById('q-input').focus();

    if (mode === 'ruen') {
        document.getElementById('q-question').innerText = currentWord.translation;
    } else {
        document.getElementById('q-question').innerText = currentWord.word;
        document.getElementById('q-transcription').innerText = currentWord.transcription;
    }
}

document.getElementById('q-input').onkeydown = e => {
    if (e.key === 'Enter') check();
};

function check() {
    const val = document.getElementById('q-input').value.trim().toLowerCase();
    const correct = mode === 'ruen'
        ? currentWord.word.toLowerCase()
        : currentWord.translation.toLowerCase();
    const ok = val === correct;

    let feedback = ok ? '✅ Верно' : '❌ Ошибка';

    if (mode === 'ruen') {
        feedback += `<br><b>${currentWord.word}</b> ${currentWord.transcription || ''}`;
        document.getElementById('q-feedback').innerHTML = feedback;

        let actions = `<button class="btn btn-outline" onclick="sayCurrent()">🔊</button>`;

        if (ok) {
            // Оборачиваем кнопки в div class="btn-group" для ряда
            actions += `
                <p>Произнесли верно?</p>
                <div class="btn-group">
                    <button class="btn btn-blue" onclick="step(true)">Да</button>
                    <button class="btn btn-outline" onclick="step(false)">Нет</button>
                </div>
            `;
        } else {
            actions += `<button class="btn btn-blue" onclick="step(false)">Далее</button>`;
        }

        document.getElementById('q-actions').innerHTML = actions;
        return;
    }

    if (mode === 'enru') {
        let actions = '';
        if (!ok) {
            feedback += `<br><b>${currentWord.word}</b> — ${currentWord.translation}`;
            actions = `
                <div class="btn-group">
                    <button class="btn btn-outline" onclick="forceCorrect()">Я был прав</button>
                    <button class="btn btn-blue" onclick="step(false)">Далее</button>
                </div>
            `;
        } else {
            actions = `<button class="btn btn-blue" onclick="step(true)">Далее</button>`;
        }
        document.getElementById('q-feedback').innerHTML = feedback;
        document.getElementById('q-actions').innerHTML = actions;
    }
}

function forceCorrect() {
    attempts[currentWord.word] = 1;
    step(true);
}

function step(success) {
    const w = queue.shift();

    if (success) {
        solvedCount++;
        results.push({ ...w, final: attempts[w.word] });
        fetch(`/save_result/${mode}`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ word: w.word, attempts: attempts[w.word] })
        });
        saveProgress();
    } else {
        attempts[w.word]++;
        queue.push(w);
    }

    render();
}

function sayCurrent() {
    const u = new SpeechSynthesisUtterance(currentWord.word);
    u.lang = 'en-US';
    speechSynthesis.speak(u);
}

function showResults() {
    document.getElementById('quiz').classList.add('hidden');
    document.getElementById('q-counter').classList.add('hidden'); // Прячем счетчик
    document.getElementById('results').classList.remove('hidden');

    const body = document.getElementById('res-body');
    body.innerHTML = '';

    results.forEach(r => {
        body.innerHTML += `
        <tr>
            <td>${r.word}</td>
            <td>${r.translation}</td>
            <td>${r.transcription || ''}</td>
            <td>${r.final}</td>
        </tr>`;
    });
}

document.getElementById('finishLaterBtn').addEventListener('click', () => {
    saveProgress();
    window.location.href = '/';
});

const nextBtn = document.getElementById('nextBtn');
if (nextBtn) {
    nextBtn.addEventListener('click', () => {
        check();
    });
}

function saveProgress() {
    const remainingWords = queue.map(w => ({
        ...w,
        attempts: attempts[w.word] || 1
    }));

    fetch(`/finish_later/${mode}`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ words: remainingWords })
    });
}
