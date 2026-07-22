// ==========================================================
// Elements
// ==========================================================

const questionInput = document.getElementById("question");

const askButton = document.getElementById("askBtn");

const entity = document.getElementById("entity");

const matched = document.getElementById("matched");

const context = document.getElementById("context");

const answer = document.getElementById("answer");


// ==========================================================
// Ask GraphRAG
// ==========================================================

async function askQuestion() {

    const question = questionInput.value.trim();

    if (question === "") {

        alert("Please enter a question.");

        return;
    }

    askButton.disabled = true;

    askButton.innerText = "Thinking...";

    answer.innerHTML = "Generating answer...";

    entity.innerText = "-";

    matched.innerText = "-";

    context.innerText = "";

    try {

        const response = await fetch("/ask", {

            method: "POST",

            headers: {

                "Content-Type": "application/json"

            },

            body: JSON.stringify({

                question: question

            })

        });

        if (!response.ok) {

            const error = await response.json();

            throw new Error(error.detail);

        }

        const data = await response.json();

        entity.innerText = data.entity;

        matched.innerText = data.matched_entity;

        context.innerText = data.context;

        answer.innerText = data.answer;

    }

    catch (error) {

        answer.innerHTML =

            "<span style='color:red'>" +

            error.message +

            "</span>";

    }

    finally {

        askButton.disabled = false;

        askButton.innerText = "Ask";

    }

}


// ==========================================================
// Events
// ==========================================================

askButton.addEventListener(

    "click",

    askQuestion

);


questionInput.addEventListener(

    "keydown",

    function (event) {

        if (

            event.key === "Enter"

            &&

            !event.shiftKey

        ) {

            event.preventDefault();

            askQuestion();

        }

    }

);