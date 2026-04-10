let timeLeft = 600; // 10 minutes in seconds
let currentQuestion = 0;
let questions = [];
let userResponses = [];

// Timer Function
function startTimer() {
    let timer = setInterval(() => {
        timeLeft--;
        let minutes = Math.floor(timeLeft / 60);
        let seconds = timeLeft % 60;
        document.getElementById("time").textContent = `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;

        if (timeLeft <= 0) {
            clearInterval(timer);
            alert("Time's up! Submitting responses...");
            submitInterview();
        }
    }, 1000);
}

// Store Answer and Move to Next
function nextQuestion() {
    let textAnswer = document.getElementById("text-answer").value;
    userResponses.push({ question: questions[currentQuestion], answer: textAnswer });
    currentQuestion++;
    document.getElementById("text-answer").value = ""; // Clear input
    showQuestion();
}

// Submit Interview
async function submitInterview() {
    let response = await fetch("/submit_interview", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ responses: userResponses })
    });
    let result = await response.json();
    alert(`Interview complete! Your score: ${result.score}/10`);
}

// Event Listeners
document.getElementById("next-btn").addEventListener("click", nextQuestion);

// Start
startTimer();
loadQuestions();
