const name = prompt("Entrez votre nom:");
const ws = new WebSocket("ws://localhost:8000/ws/quiz");

ws.onopen = () => ws.send(name);

const artistEl = document.getElementById("artist");
const titleEl = document.getElementById("title");
const questionEl = document.getElementById("question");
const logEl = document.getElementById("log");
const timerBar = document.getElementById("timer");
const playerCountEl = document.getElementById("player-count");
const scoreboardEl = document.getElementById("scoreboard");

let countdownInterval = null;
const QUESTION_TIME = 15; // secondes

ws.onopen = () => ws.send(name);

const btnNext = document.getElementById("next-question");
const answerInput = document.createElement("input");
document.body.appendChild(answerInput);

btnNext.addEventListener("click", () => ws.send(JSON.stringify({action:"next_question"})));
answerInput.addEventListener("keypress", e => {
    if(e.key === "Enter") {
        ws.send(JSON.stringify({action:"answer", answer: answerInput.value}));
        answerInput.value = "";
    }
});

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if(data.song && data.question){
        document.getElementById("artist").textContent = data.song.artist;
        document.getElementById("title").textContent = data.song.title;
        document.getElementById("question").textContent = data.question.lyrics ? data.question.lyrics.join("\n") : "🎧 Écoutez l'audio";
    }
    if(data.scores){
        const sb = document.getElementById("scoreboard");
        sb.innerHTML = "";
        data.scores.forEach(p => {
            const li = document.createElement("li");
            li.textContent = `${p.name}: ${p.score} pts`;
            sb.appendChild(li);
        });
    }
};

btnNext.addEventListener("click", () => {
    ws.send("next_question");
});

function log(msg){
    const p = document.createElement("p");
    p.textContent = msg;
    logEl.appendChild(p);
    logEl.scrollTop = logEl.scrollHeight;
}

// Animation des paroles
function animateLyrics(lines) {
    questionEl.textContent = "";
    let idx = 0;
    function showLine() {
        if(idx < lines.length){
            questionEl.textContent += lines[idx] + "\n";
            idx++;
            setTimeout(showLine, 1000);
        }
    }
    showLine();
}

// Timer visuel
function startTimer(seconds) {
    clearInterval(countdownInterval);
    timerBar.style.width = "100%";
    let timeLeft = seconds;
    countdownInterval = setInterval(() => {
        timeLeft--;
        timerBar.style.width = `${(timeLeft / seconds) * 100}%`;
        if(timeLeft <= 0) clearInterval(countdownInterval);
    }, 1000);
}

// Mettre à jour les joueurs
function updatePlayers(players) {
    playerCountEl.textContent = `Joueurs connectés: ${players}`;
}

// Mettre à jour le classement
function updateScoreboard(scores) {
    scoreboardEl.innerHTML = "";
    for(const player of scores){
        const li = document.createElement("li");
        li.textContent = `${player.name}: ${player.score} pts`;
        scoreboardEl.appendChild(li);
    }
}
