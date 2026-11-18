// BharatPilot Interactive Client Logic
document.addEventListener("DOMContentLoaded", () => {
  // 1. Tab Switching
  const navTabs = document.querySelectorAll(".nav-tab");
  const tabContents = document.querySelectorAll(".tab-content");

  navTabs.forEach(btn => {
    btn.addEventListener("click", () => {
      navTabs.forEach(b => b.classList.remove("active"));
      tabContents.forEach(c => c.classList.remove("active"));
      btn.classList.add("active");
      const target = document.getElementById(btn.getAttribute("data-tab"));
      if (target) target.classList.add("active");
    });
  });

  // 2. Travel Subnav Mode
  let currentTravelMode = "flights";
  const subnavBtns = document.querySelectorAll(".subnav-btn");
  subnavBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      subnavBtns.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      currentTravelMode = btn.getAttribute("data-mode");
      updateTravelInputLabels();
      fetchTravelResults();
    });
  });

  function updateTravelInputLabels() {
    const origInput = document.getElementById("travel-origin");
    const destInput = document.getElementById("travel-dest");
    const title = document.getElementById("results-title");

    if (currentTravelMode === "flights") {
      origInput.value = "DEL";
      destInput.value = "BLR";
      title.innerText = "Available Flights & Fares";
    } else if (currentTravelMode === "hotels") {
      origInput.value = "DEL";
      destInput.value = "GOA";
      title.innerText = "Hotels & Heritage Homestays in Goa";
    } else if (currentTravelMode === "trains") {
      origInput.value = "NDLS";
      destInput.value = "MMCT";
      title.innerText = "IRCTC Trains & Live Berths";
    } else if (currentTravelMode === "buses") {
      origInput.value = "BLR";
      destInput.value = "HYD";
      title.innerText = "Intercity AC Sleeper Buses";
    }
  }

  // 3. Travel Search
  document.getElementById("btn-search-travel").addEventListener("click", fetchTravelResults);

  async function fetchTravelResults() {
    const origin = document.getElementById("travel-origin").value.trim();
    const dest = document.getElementById("travel-dest").value.trim();
    const cardsContainer = document.getElementById("travel-cards");
    const countBadge = document.getElementById("results-count");

    cardsContainer.innerHTML = '<div style="color:#86868b; padding:2rem; text-align:center;">Searching live options...</div>';

    try {
      if (currentTravelMode === "flights") {
        const res = await fetch(`/api/flights?origin=${origin}&destination=${dest}`);
        const data = await res.json();
        countBadge.innerText = `${data.length} flights found`;
        renderFlights(data);
      } else if (currentTravelMode === "hotels") {
        const res = await fetch(`/api/hotels?city=${dest}`);
        const data = await res.json();
        countBadge.innerText = `${data.length} properties found`;
        renderHotels(data);
      } else if (currentTravelMode === "trains") {
        const res = await fetch(`/api/trains?origin=${origin}&destination=${dest}`);
        const data = await res.json();
        countBadge.innerText = `${data.length} trains found`;
        renderTrains(data);
      } else if (currentTravelMode === "buses") {
        const res = await fetch(`/api/buses?origin=${origin}&destination=${dest}`);
        const data = await res.json();
        countBadge.innerText = `${data.length} buses found`;
        renderBuses(data);
      }
    } catch (e) {
      cardsContainer.innerHTML = `<div style="color:#ff453a; padding:1.5rem;">Error loading results: ${e.message}</div>`;
    }
  }

  function renderFlights(flights) {
    const container = document.getElementById("travel-cards");
    container.innerHTML = "";

    flights.forEach(f => {
      const card = document.createElement("div");
      card.className = "travel-card";
      card.innerHTML = `
        <div class="t-info">
          <div class="t-title">${f.airline} &bull; ${f.flight_number}</div>
          <div class="t-sub">${f.origin} (${f.departure_time}) &rarr; ${f.destination} (${f.arrival_time}) &bull; ${f.duration} (${f.stops === 0 ? "Non-stop" : f.stops + " stop"})</div>
          <div class="t-badges">
            <span class="badge-tag">Cabin: ${f.cabin_baggage}</span>
            <span class="badge-tag">Check-in: ${f.checkin_baggage}</span>
            ${f.is_cheapest ? '<span class="badge-tag cheapest">Lowest Fare</span>' : ''}
          </div>
        </div>
        <div class="t-right">
          <div class="t-price">&#8377;${f.price_inr.toLocaleString()}<span>per adult</span></div>
          <button class="btn-primary btn-book-flight" data-item='${JSON.stringify(f)}'>Book &rarr;</button>
        </div>
      `;
      container.appendChild(card);
    });

    document.querySelectorAll(".btn-book-flight").forEach(b => {
      b.addEventListener("click", () => {
        const item = JSON.parse(b.getAttribute("data-item"));
        openPaymentModal("flight", item);
      });
    });
  }

  function renderHotels(hotels) {
    const container = document.getElementById("travel-cards");
    container.innerHTML = "";

    hotels.forEach(h => {
      const card = document.createElement("div");
      card.className = "travel-card";
      card.innerHTML = `
        <div class="t-info">
          <div class="t-title">${h.name} &bull; ${h.property_type}</div>
          <div class="t-sub">${h.location} &bull; &#9733; ${h.user_rating}/5.0 (${h.reviews_count.toLocaleString()} reviews)</div>
          <div class="t-badges">
            ${h.couple_friendly ? '<span class="badge-tag cheapest">Couple Friendly</span>' : ''}
            ${h.free_cancellation ? '<span class="badge-tag">Free Cancellation</span>' : ''}
            <span class="badge-tag">${h.amenities.slice(0, 2).join(", ")}</span>
          </div>
        </div>
        <div class="t-right">
          <div class="t-price">&#8377;${h.price_per_night_inr.toLocaleString()}<span>per night</span></div>
          <button class="btn-primary btn-book-hotel" data-item='${JSON.stringify(h)}'>Book &rarr;</button>
        </div>
      `;
      container.appendChild(card);
    });

    document.querySelectorAll(".btn-book-hotel").forEach(b => {
      b.addEventListener("click", () => {
        const item = JSON.parse(b.getAttribute("data-item"));
        openPaymentModal("hotel", item);
      });
    });
  }

  function renderTrains(trains) {
    const container = document.getElementById("travel-cards");
    container.innerHTML = "";

    trains.forEach(t => {
      const card = document.createElement("div");
      card.className = "travel-card";
      const classesStr = Object.entries(t.classes_available).map(([k, v]) => `<strong>${k}:</strong> ${v}`).join(" &bull; ");
      card.innerHTML = `
        <div class="t-info">
          <div class="t-title">${t.train_number} &bull; ${t.train_name}</div>
          <div class="t-sub">${t.origin_station} (${t.departure_time}) &rarr; ${t.destination_station} (${t.arrival_time}) &bull; ${t.travel_time}</div>
          <div class="t-badges" style="margin-top:0.5rem; font-size:0.85rem; color:#bbb;">
            ${classesStr}
          </div>
        </div>
        <div class="t-right">
          <div class="t-price">&#8377;${(Object.values(t.base_fare_inr)[0] || 1500).toLocaleString()}<span>starting fare</span></div>
          <button class="btn-primary" onclick="alert('IRCTC Tatkal booking window opens at 10:00 AM for AC classes and 11:00 AM for Non-AC. Passenger profile ready for 1-click booking.')">IRCTC Book &rarr;</button>
        </div>
      `;
      container.appendChild(card);
    });
  }

  function renderBuses(buses) {
    const container = document.getElementById("travel-cards");
    container.innerHTML = "";

    buses.forEach(b => {
      const card = document.createElement("div");
      card.className = "travel-card";
      card.innerHTML = `
        <div class="t-info">
          <div class="t-title">${b.operator} &bull; ${b.bus_type}</div>
          <div class="t-sub">${b.origin} (${b.departure_time}) &rarr; ${b.destination} (${b.arrival_time}) &bull; ${b.duration}</div>
          <div class="t-badges">
            <span class="badge-tag cheapest">&#9733; ${b.rating} Rating</span>
            <span class="badge-tag">${b.seats_left} seats left</span>
            <span class="badge-tag">${b.boarding_point}</span>
          </div>
        </div>
        <div class="t-right">
          <div class="t-price">&#8377;${b.price_inr.toLocaleString()}<span>per seat</span></div>
          <a href="${b.booking_url}" target="_blank" class="btn-primary" style="text-decoration:none;">Book &rarr;</a>
        </div>
      `;
      container.appendChild(card);
    });
  }

  // 4. Booking Handoff Modal
  async function openPaymentModal(type, item) {
    const payload = (type === "hotel")
      ? { type: "hotel", hotel_name: item.name, city: item.city, nights: 1, price: item.price_per_night_inr }
      : { type: "flight", airline: item.airline, flight_number: item.flight_number, origin: item.origin, destination: item.destination, fare: item.price_inr };

    try {
      const res = await fetch("/api/booking/handoff", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const sess = await res.json();

      document.getElementById("modal-item-title").innerHTML = sess.item_title;
      document.getElementById("m-pax-name").innerText = sess.passenger_name;
      document.getElementById("m-pax-age").innerText = sess.passenger_age;
      document.getElementById("m-pax-gender").innerText = sess.passenger_gender;
      document.getElementById("m-pax-email").innerText = sess.contact_email;
      document.getElementById("m-pax-phone").innerText = sess.contact_phone;
      document.getElementById("m-sess-id").innerText = sess.session_id;

      document.getElementById("m-base-fare").innerText = `₹${sess.amount_inr.toLocaleString()}`;
      document.getElementById("m-taxes").innerText = `₹${sess.taxes_inr.toLocaleString()}`;
      document.getElementById("m-conv-fee").innerText = `₹${sess.convenience_fee_inr.toLocaleString()}`;
      document.getElementById("m-total-amt").innerText = `₹${sess.total_payable_inr.toLocaleString()}`;

      document.getElementById("btn-goto-payment").href = sess.payment_gateway_url;

      document.getElementById("booking-modal").classList.add("open");
    } catch (e) {
      alert("Handoff session error: " + e.message);
    }
  }

  document.getElementById("btn-close-modal").addEventListener("click", () => {
    document.getElementById("booking-modal").classList.remove("open");
  });

  // 5. ITR Optimizer Execution
  let lastITRJson = null;
  document.getElementById("btn-calc-itr").addEventListener("click", async () => {
    const salary = parseInt(document.getElementById("itr-salary").value) || 0;
    const tds = parseInt(document.getElementById("itr-tds").value) || 0;
    const sec80c = parseInt(document.getElementById("itr-80c").value) || 0;
    const sec80d = parseInt(document.getElementById("itr-80d").value) || 0;
    const hra = parseInt(document.getElementById("itr-hra").value) || 0;
    const pan = document.getElementById("itr-pan").value.trim();

    try {
      const res = await fetch("/api/itr/optimize", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          gross_salary: salary,
          tds: tds,
          sec_80c: sec80c,
          sec_80d: sec80d,
          hra: hra,
          pan: pan,
          name: "Shubhransh Gupta"
        })
      });
      const data = await res.json();
      lastITRJson = data.itr_1_json;

      const resultsDiv = document.getElementById("itr-results");
      resultsDiv.style.display = "block";

      const banner = document.getElementById("showdown-banner");
      const isNew = data.recommended_regime === "NEW_REGIME";
      banner.innerHTML = `🏆 Recommended: <strong>${isNew ? "New Tax Regime" : "Old Tax Regime"}</strong> &bull; You save <strong>₹${data.tax_savings_inr.toLocaleString()}</strong> in tax!`;

      document.getElementById("stat-new-tax").innerText = `₹${data.new_regime.total_tax_payable.toLocaleString()}`;
      document.getElementById("stat-new-deductions").innerText = `Std Deduction: ₹${data.new_regime.exemptions_and_deductions.toLocaleString()} | Taxable: ₹${data.new_regime.net_taxable_income.toLocaleString()}`;

      document.getElementById("stat-old-tax").innerText = `₹${data.old_regime.total_tax_payable.toLocaleString()}`;
      document.getElementById("stat-old-deductions").innerText = `Total Deductions: ₹${data.old_regime.exemptions_and_deductions.toLocaleString()} | Taxable: ₹${data.old_regime.net_taxable_income.toLocaleString()}`;

      document.getElementById("box-new-regime").className = isNew ? "regime-box winner" : "regime-box";
      document.getElementById("box-old-regime").className = !isNew ? "regime-box winner" : "regime-box";
    } catch (e) {
      alert("ITR calculation error: " + e.message);
    }
  });

  document.getElementById("btn-download-itr").addEventListener("click", () => {
    if (!lastITRJson) return;
    const blob = new Blob([JSON.stringify(lastITRJson, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "ITR1_Sahaj_2024_25.json";
    a.click();
    URL.revokeObjectURL(url);
  });

  // 6. EPF Explorer Execution
  document.getElementById("btn-explore-epf").addEventListener("click", async () => {
    const basic = parseInt(document.getElementById("epf-basic").value) || 50000;
    const tenure = parseFloat(document.getElementById("epf-tenure").value) || 4.0;
    const balance = parseInt(document.getElementById("epf-balance").value) || 350000;

    try {
      const res = await fetch(`/api/epf?basic=${basic}&tenure=${tenure}&balance=${balance}`);
      const data = await res.json();

      document.getElementById("epf-results").style.display = "block";
      document.getElementById("val-emp-share").innerText = `₹${data.summary.employee_share_balance_inr.toLocaleString()}`;
      document.getElementById("val-empr-share").innerText = `₹${data.summary.employer_share_balance_inr.toLocaleString()}`;
      document.getElementById("val-eps-share").innerText = `₹${data.summary.pension_scheme_balance_inr.toLocaleString()}`;
      document.getElementById("val-total-epf").innerText = `₹${data.summary.total_epf_balance_inr.toLocaleString()}`;

      // Rules
      const rulesList = document.getElementById("epf-rules-list");
      rulesList.innerHTML = `
        <li><strong>Form 31 (Medical):</strong> ${data.eligibility.form_31_medical.rule}</li>
        <li><strong>Form 31 (Housing):</strong> ${data.eligibility.form_31_housing.eligible ? "✅ ELIGIBLE &mdash; " : "❌ NOT ELIGIBLE &mdash; "}${data.eligibility.form_31_housing.rule}</li>
        <li><strong>Form 31 (Marriage):</strong> ${data.eligibility.form_31_marriage.eligible ? "✅ ELIGIBLE &mdash; " : "❌ NOT ELIGIBLE &mdash; "}${data.eligibility.form_31_marriage.rule}</li>
        <li><strong>Form 19 (Full PF Settlement):</strong> ${data.eligibility.form_19_full_settlement.rule}</li>
        <li><strong>Form 10C (Pension):</strong> ${data.eligibility.form_10c_pension.rule}</li>
      `;

      // Corpus
      document.getElementById("val-corpus").innerText = `₹${data.projection.projected_corpus_at_58_inr.toLocaleString()}`;
    } catch (e) {
      alert("EPF fetch error: " + e.message);
    }
  });

  // Initial load
  fetchTravelResults();
});
