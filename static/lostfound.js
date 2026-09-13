(() => {
    "use strict";

    const todayLabel = () =>
        new Date().toLocaleDateString("en-GB", { day: "2-digit", month: "short", year: "numeric" });

    // Seed data matches the original mockup so the page isn't empty on first load.
    let lostItems = [
        {
            item: "Mobile Phone",
            location: "Library",
            date: "12 Sept 2026",
            description: "Black phone with blue cover",
            contact: "98XXXXXXXX",
            icon: "📱"
        }
    ];

    let foundItems = [
        {
            item: "Wireless Earbuds",
            location: "CSE Block",
            date: "12 Sept 2026",
            description: "Left in the charging case, no name tag.",
            contact: "98XXXXXXXX",
            icon: "🎧"
        }
    ];

    // Handover history: who a found item was given to, with their ID card photo.
    let history = [];

    const ICONS = ["📱", "🎧", "🔑", "🎒", "📘", "💳", "🧢", "☂️", "🖊️", "🧾"];
    const pickIcon = () => ICONS[Math.floor(Math.random() * ICONS.length)];

    const lostList = document.getElementById("lostList");
    const foundList = document.getElementById("foundList");
    const historyList = document.getElementById("historyList");
    const lostEmpty = document.getElementById("lostEmpty");
    const foundEmpty = document.getElementById("foundEmpty");
    const historyEmpty = document.getElementById("historyEmpty");
    const lostCount = document.getElementById("lostCount");
    const foundCount = document.getElementById("foundCount");
    const historyCount = document.getElementById("historyCount");

    let claimingIndex = null; // index into foundItems currently being handed over

    function escapeHtml(str) {
        const div = document.createElement("div");
        div.textContent = str;
        return div.innerHTML;
    }

    function itemCard(entry, kind, index) {
        const card = document.createElement("div");
        card.className = "lf-item-card";

        const main = document.createElement("div");
        main.className = "lf-item-main";
        main.innerHTML = `
            <strong>${entry.icon} ${escapeHtml(entry.item)}</strong>
            <div class="lf-item-meta">
                <span>📍 ${kind === "lost" ? "Lost" : "Found"} near ${escapeHtml(entry.location)}</span>
                <span>📅 ${escapeHtml(entry.date)}</span>
            </div>
        `;
        card.appendChild(main);

        if (kind === "lost") {
            const btn = document.createElement("button");
            btn.className = "lf-item-btn";
            btn.type = "button";
            btn.textContent = "View Details";
            btn.addEventListener("click", () => showDetail(entry, kind));
            card.appendChild(btn);
        } else {
            const actions = document.createElement("div");
            actions.className = "lf-item-actions";

            const callBtn = document.createElement("button");
            callBtn.className = "lf-item-btn";
            callBtn.type = "button";
            callBtn.textContent = "Call Finder";
            callBtn.addEventListener("click", () => {
                window.location.href = `tel:${entry.contact}`;
            });

            const claimBtn = document.createElement("button");
            claimBtn.className = "lf-item-btn";
            claimBtn.type = "button";
            claimBtn.textContent = "Mark as Given";
            claimBtn.addEventListener("click", () => openClaim(index));

            actions.append(callBtn, claimBtn);
            card.appendChild(actions);
        }

        return card;
    }

    function historyCard(entry) {
        const card = document.createElement("div");
        card.className = "lf-item-card lf-history-card";

        const photo = document.createElement("img");
        photo.className = "lf-history-photo";
        photo.src = entry.photoDataUrl;
        photo.alt = `ID card photo of ${entry.claimedBy}`;

        const main = document.createElement("div");
        main.className = "lf-item-main";
        main.innerHTML = `
            <strong>${entry.icon} ${escapeHtml(entry.item)}</strong>
            <div class="lf-history-meta">Given to ${escapeHtml(entry.claimedBy)} · ${escapeHtml(entry.date)}</div>
        `;

        const status = document.createElement("span");
        status.className = "lf-status-given";
        status.textContent = "Given";

        card.append(photo, main, status);
        return card;
    }

    function render() {
        lostList.innerHTML = "";
        foundList.innerHTML = "";
        historyList.innerHTML = "";

        lostItems.forEach((entry, i) => lostList.appendChild(itemCard(entry, "lost", i)));
        foundItems.forEach((entry, i) => foundList.appendChild(itemCard(entry, "found", i)));
        history.forEach((entry) => historyList.appendChild(historyCard(entry)));

        lostEmpty.classList.toggle("lf-show", lostItems.length === 0);
        foundEmpty.classList.toggle("lf-show", foundItems.length === 0);
        historyEmpty.classList.toggle("lf-show", history.length === 0);

        lostCount.textContent = `${lostItems.length} reported`;
        foundCount.textContent = `${foundItems.length} reported`;
        historyCount.textContent = `${history.length} items`;
    }

    // Modal open/close
    function openOverlay(id) {
        document.getElementById(id).classList.add("lf-open");
    }
    function closeOverlay(id) {
        document.getElementById(id).classList.remove("lf-open");
    }

    document.getElementById("openLostForm").addEventListener("click", () => openOverlay("lostOverlay"));
    document.getElementById("openFoundForm").addEventListener("click", () => openOverlay("foundOverlay"));

    document.querySelectorAll("[data-close]").forEach((btn) => {
        btn.addEventListener("click", () => closeOverlay(btn.dataset.close));
    });

    document.querySelectorAll(".lf-overlay").forEach((overlay) => {
        overlay.addEventListener("click", (e) => {
            if (e.target === overlay) overlay.classList.remove("lf-open");
        });
    });

    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape") {
            document.querySelectorAll(".lf-overlay.lf-open").forEach((o) => o.classList.remove("lf-open"));
        }
    });

    // Detail modal
    function showDetail(entry, kind) {
        document.getElementById("detailTitle").textContent = `${entry.icon} ${entry.item}`;
        document.getElementById("detailBody").innerHTML = `
            <dt>Status</dt><dd>${kind === "lost" ? "Lost" : "Found"}</dd>
            <dt>Location</dt><dd>${escapeHtml(entry.location)}</dd>
            <dt>Date</dt><dd>${escapeHtml(entry.date)}</dd>
            <dt>Description</dt><dd>${escapeHtml(entry.description)}</dd>
            <dt>Contact</dt><dd>${escapeHtml(entry.contact)}</dd>
        `;
        openOverlay("detailOverlay");
    }

    // Claim / handover modal
    const claimForm = document.getElementById("claimForm");
    const claimPhotoInput = claimForm.querySelector('input[name="idCard"]');
    const claimPhotoPreview = document.getElementById("claimPhotoPreview");

    function openClaim(index) {
        claimingIndex = index;
        const entry = foundItems[index];
        document.getElementById("claimItemLabel").textContent =
            `${entry.icon} ${entry.item} — found near ${entry.location}`;
        claimForm.reset();
        claimPhotoPreview.innerHTML = "";
        claimPhotoPreview.classList.remove("lf-show");
        openOverlay("claimOverlay");
    }

    claimPhotoInput.addEventListener("change", () => {
        const file = claimPhotoInput.files[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = () => {
            claimPhotoPreview.innerHTML = `<img src="${reader.result}" alt="ID card preview">`;
            claimPhotoPreview.classList.add("lf-show");
        };
        reader.readAsDataURL(file);
    });

    claimForm.addEventListener("submit", (e) => {
        e.preventDefault();
        if (claimingIndex === null) return;

        const file = claimPhotoInput.files[0];
        const fd = new FormData(claimForm);
        const entry = foundItems[claimingIndex];

        const finish = (photoDataUrl) => {
            history.unshift({
                item: entry.item,
                icon: entry.icon,
                location: entry.location,
                claimedBy: fd.get("claimantName"),
                photoDataUrl,
                date: todayLabel()
            });
            foundItems.splice(claimingIndex, 1);
            claimingIndex = null;
            closeOverlay("claimOverlay");
            render();
        };

        if (file) {
            const reader = new FileReader();
            reader.onload = () => finish(reader.result);
            reader.readAsDataURL(file);
        } else {
            finish("");
        }
    });

    // Form submissions
    document.getElementById("lostForm").addEventListener("submit", (e) => {
        e.preventDefault();
        const fd = new FormData(e.target);
        lostItems.unshift({
            item: fd.get("item"),
            location: fd.get("location"),
            description: fd.get("description"),
            contact: fd.get("contact"),
            date: todayLabel(),
            icon: pickIcon()
        });
        e.target.reset();
        closeOverlay("lostOverlay");
        render();
    });

    document.getElementById("foundForm").addEventListener("submit", (e) => {
        e.preventDefault();
        const fd = new FormData(e.target);
        foundItems.unshift({
            item: fd.get("item"),
            location: fd.get("location"),
            description: fd.get("description"),
            contact: fd.get("contact"),
            date: todayLabel(),
            icon: pickIcon()
        });
        e.target.reset();
        closeOverlay("foundOverlay");
        render();
    });

    render();
})();