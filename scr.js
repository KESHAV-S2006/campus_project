/* ================= SEARCH ================= */

const searchInput = document.getElementById("serviceSearch");
const searchBtn = document.getElementById("searchBtn");

const cards = document.querySelectorAll(".service-card");

const serviceCount = document.getElementById("serviceCount");
const noResults = document.getElementById("noResults");


function filterServices() {

    const query =
        searchInput.value
        .toLowerCase()
        .trim();

    let visibleCards = 0;


    cards.forEach(card => {

        const name =
            card.dataset.name.toLowerCase();

        const description =
            card.dataset.description.toLowerCase();


        const matches =
            name.includes(query) ||
            description.includes(query);


        if (matches) {

            card.style.display = "";

            visibleCards++;

        } else {

            card.style.display = "none";

        }

    });


    /* UPDATE COUNTER */

    if (visibleCards === 1) {

        serviceCount.textContent =
            "1 service found";

    } else {

        serviceCount.textContent =
            `${visibleCards} services available`;

    }


    /* NO RESULT MESSAGE */

    if (visibleCards === 0) {

        noResults.classList.add("show");

    } else {

        noResults.classList.remove("show");

    }

}


/* Search while typing */

searchInput.addEventListener(
    "input",
    filterServices
);


/* Search button */

searchBtn.addEventListener(
    "click",
    filterServices
);


/* Enter key */

searchInput.addEventListener(
    "keydown",
    function(event) {

        if (event.key === "Enter") {

            filterServices();

        }

    }
);


/* ================= SERVICE BUTTONS ================= */

const serviceButtons =
    document.querySelectorAll(".service-btn");


serviceButtons.forEach(button => {

    button.addEventListener(
        "click",
        function() {

            const card =
                this.closest(".service-card");

            const serviceName =
                card.querySelector("h3").textContent;


            /*
             * Temporary behavior.
             *
             * Later replace this alert with:
             *
             * window.location.href = "lost-found.html";
             *
             * etc.
             */

            alert(
                `Opening ${serviceName}...`
            );

        }
    );

});


/* ================= EXPLORE BUTTON ================= */

const exploreBtn =
    document.getElementById("exploreBtn");


exploreBtn.addEventListener(
    "click",
    function() {

        document
            .getElementById("services")
            .scrollIntoView({
                behavior: "smooth"
            });

    }
);
/* ================= LOGOUT ================= */

const logoutBtn =
    document.getElementById("logoutBtn");


logoutBtn.addEventListener(
    "click",
    function() {

        const confirmLogout =
            confirm(
                "Are you sure you want to logout?"
            );


        if (confirmLogout) {

            window.location.href =
                "login.html";

        }

    }
);