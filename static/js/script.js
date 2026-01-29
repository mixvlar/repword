let queue = [];
let attempts = {};
let results = [];

const mode = document.querySelector('.card').dataset.mode;
let currentWord = null;

async function start() {
    const res = await fetch(`/get_words/${mode}`);
    queue = await res.json();

    // Восстанавливаем attempts
    queue.forEach(w => attempts[w.word] = w.attempts || 1);

    document.getElementById('start-screen').classList.add('hidden');
    document.getElementById('quiz').classList.remove('hidden');
    render();
}

// ---------------------------
function render() {
    if (queue.length === 0) return showResults();

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

// ---------------------------
document.getElementById('q-input').onkeydown = e => {
    if (e.key === 'Enter') check();
};

// ---------------------------
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
            actions += `
                <p>Произнесли верно?</p>
                <button class="btn btn-blue" onclick="step(true)">Да</button>
                <button class="btn btn-outline" onclick="step(false)">Нет</button>
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
            // Кнопка "Я был прав" появляется ТОЛЬКО при ошибке в режиме EN->RU
            actions = `
                <button class="btn btn-outline" onclick="forceCorrect()">Я был прав</button>
                <button class="btn btn-blue" onclick="step(false)">Далее</button>
            `;
        } else {
            actions = `<button class="btn btn-blue" onclick="step(true)">Далее</button>`;
        }
        document.getElementById('q-feedback').innerHTML = feedback;
        document.getElementById('q-actions').innerHTML = actions;
    }
}

// Принудительное зачисление верного ответа
function forceCorrect() {
    attempts[currentWord.word] = 1; // Сбрасываем счетчик попыток на 1
    step(true);
}

// ---------------------------
function step(success) {
    const w = queue.shift();

    if (success) {
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

// ---------------------------
function showResults() {
    document.getElementById('quiz').classList.add('hidden');
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

// ---------------------------
document.getElementById('finishLaterBtn').addEventListener('click', () => {
    saveProgress();
    window.location.href = '/';
});

document.getElementById('nextBtn').addEventListener('click', () => {
    check();
});

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
