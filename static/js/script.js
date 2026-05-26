let queue = [];
let attempts = {};
let results = [];
let totalWords = 0;
let solvedCount = 0;
const mode = document.querySelector(".card").dataset.mode;
let currentWord = null;

async function start() {
    const res = await fetch(`/get_words/${mode}`);
    const data = await res.json();

    if (!data || data.length === 0) {
        window.location.replace("/");
        return;
    }

    queue = data;
    totalWords = queue.length;
    solvedCount = 0;
    results = [];
    attempts = {};

    queue.forEach((w) => {
        attempts[w.word] = 1;
    });

    document.getElementById("start-screen").classList.add("hidden");
    const counterEl = document.getElementById("q-counter");
    if (counterEl) counterEl.classList.remove("hidden");
    document.getElementById("quiz").classList.remove("hidden");
    render();
}

function render() {
    if (queue.length === 0) return showResults();

    const counterEl = document.getElementById("q-counter");
    if (counterEl) counterEl.innerText = `${solvedCount} / ${totalWords}`;

    const rawWord = queue[0];
    currentWord = JSON.parse(JSON.stringify(rawWord));

    document.getElementById("q-input").value = "";
    document.getElementById("q-feedback").innerHTML = "";
    document.getElementById("q-actions").innerHTML = "";
    document.getElementById("q-input").focus();

    if (mode === "ruen") {
        document.getElementById("q-question").innerText = currentWord.translation;
        return;
    }

    document.getElementById("q-question").innerText = currentWord.word;

    const transEl = document.getElementById("q-transcription");
    if (transEl) transEl.innerText = currentWord.transcription || "";

    const extraEl = document.getElementById("q-extra-info");
    if (extraEl) {
        const useText = Array.isArray(currentWord.use)
            ? currentWord.use.join(" ")
            : (currentWord.use || "—");

        extraEl.innerHTML = `
            <div><b>Level:</b> ${currentWord.level || "—"}</div>
            <div><b>Use:</b> <i>${useText}</i></div>
        `;
    }
}

function check() {
    const val = document.getElementById("q-input").value.trim().toLowerCase();
    const correct = mode === "ruen"
        ? currentWord.word.toLowerCase()
        : currentWord.translation.toLowerCase();

    const ok = val === correct;

    let feedback = ok ? "✅ Верно" : "❌ Ошибка";
    let actions = "";

    if (mode === "ruen") {
        const useText = Array.isArray(currentWord.use)
            ? currentWord.use.join(" ")
            : (currentWord.use || "—");
        const exampleText = currentWord.example || "—";
        const explanationText = currentWord.explanation || "—";
        const extraInfo = `
            <div style="margin-top: 10px; font-size: 0.9em; color: #555;">
                <p><b>Уровень:</b> ${currentWord.level || "—"}</p>
                <p><b>Применение:</b> <i>${useText}</i></p>
                <p><b>Пояснение:</b> <i>${explanationText}</i></p>
            </div>
        `;

        feedback += `<br><b>${currentWord.word}</b> ${currentWord.transcription || ""}`;
        if (ok) {
            feedback += `${extraInfo}<div style="margin-top: 10px; font-size: 0.95em;"><b>Пример:</b> <i>${exampleText}</i></div>`;
        } else {
            feedback += extraInfo;
        }

        actions = `<button class="btn btn-outline" onclick="sayCurrent()">🔊</button>`;
        if (ok) {
            actions += `
                <p>Произнесли верно?</p>
                <div class="btn-group">
                    <button class="btn btn-blue" onclick="step(true)">Да</button>
                    <button class="btn btn-outline" onclick="step(false)">Нет</button>
                </div>`;
        } else {
            actions += `
                <div class="btn-group">
                    <button class="btn btn-outline" onclick="forceCorrect()">Я был прав</button>
                    <button class="btn btn-blue" onclick="step(false)">Далее</button>
                </div>`;
        }
    } else if (!ok) {
        feedback += `<br><b>${currentWord.word}</b> — ${currentWord.translation}`;
        actions = `
            <div class="btn-group">
                <button class="btn btn-outline" onclick="forceCorrect()">Я был прав</button>
                <button class="btn btn-blue" onclick="step(false)">Далее</button>
            </div>`;
    } else {
        actions = `<button class="btn btn-blue" onclick="step(true)">Далее</button>`;
    }

    document.getElementById("q-feedback").innerHTML = feedback;
    document.getElementById("q-actions").innerHTML = actions;
}

function forceCorrect() {
    step(true);
}

function step(success) {
    const wordKey = currentWord.word;
    const wordObj = queue.shift();

    if (success) {
        const finalAtt = attempts[wordKey];
        solvedCount++;
        results.push({ ...wordObj, final: finalAtt });

        fetch(`/save_result/${mode}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ word: wordKey, attempts: finalAtt })
        });
    } else {
        attempts[wordKey] = (attempts[wordKey] || 1) + 1;
        queue.push(wordObj);
    }

    render();
}

function sayCurrent() {
    const u = new SpeechSynthesisUtterance(currentWord.word);
    u.lang = "en-US";
    speechSynthesis.speak(u);
}

function showResults() {
    document.getElementById("quiz").classList.add("hidden");
    const counterEl = document.getElementById("q-counter");
    if (counterEl) counterEl.classList.add("hidden");
    document.getElementById("results").classList.remove("hidden");

    const body = document.getElementById("res-body");
    body.innerHTML = "";
    results.forEach((r) => {
        body.innerHTML += `
            <tr>
                <td>${r.word}</td>
                <td>${r.translation}</td>
                <td>${r.level || ""}</td>
                <td>${r.final}</td>
            </tr>`;
    });
}

document.getElementById("q-input").onkeydown = (e) => {
    if (e.key === "Enter") {
        const btn = document.querySelector("#q-actions .btn-blue");
        if (btn) btn.click();
        else check();
    }
};
