let tickersArr = [];  // Change 'const' to 'let' to allow reassignment

const generateReportBtn = document.querySelector('.generate-report-btn');
generateReportBtn.addEventListener('click', fetchStockData);

document.getElementById('ticker-input').addEventListener('input', function () {
    const query = this.value;
    if (query.length > 2) {
        fetch(`/search?keyword=${query}`)
            .then(response => response.json())
            .then(data => {
                const autocompleteList = document.getElementById('autocomplete-list');
                autocompleteList.innerHTML = '';
                if (data.error) {
                    const errorItem = document.createElement('div');
                    errorItem.textContent = data.error;
                    autocompleteList.appendChild(errorItem);
                } else {
                    data.forEach(company => {
                        const item = document.createElement('div');
                        item.textContent = `${company.name} (${company.symbol})`;
                        item.addEventListener('click', function () {
                            addCompany(company.symbol);
                            document.getElementById('ticker-input').value = '';
                            autocompleteList.innerHTML = '';
                        });
                        autocompleteList.appendChild(item);
                    });
                }
            })
            .catch(error => console.error('Error:', error));
    }
});

function addCompany(symbol) {
    if (symbol && !tickersArr.includes(symbol)) {
        tickersArr.push(symbol.toUpperCase());
        renderTickers();
    }
}

function removeCompany(symbol) {
    tickersArr = tickersArr.filter(ticker => ticker !== symbol);
    renderTickers();
}

function renderTickers() {
    const tickersDiv = document.querySelector('.ticker-choice-display');
    tickersDiv.innerHTML = '';
    tickersArr.forEach(ticker => {
        const newTickerSpan = document.createElement('span');
        newTickerSpan.textContent = ticker;
        newTickerSpan.classList.add('ticker');
        const removeBtn = document.createElement('button');
        removeBtn.textContent = 'Remove';
        removeBtn.addEventListener('click', () => removeCompany(ticker));
        newTickerSpan.appendChild(removeBtn);
        tickersDiv.appendChild(newTickerSpan);
    });
}

function fetchStockData() {
    if (tickersArr.length === 0) {
        alert("Please add at least one company.");
        return;
    }

    const symbols = tickersArr.join(',');
    fetch(`/predict?symbols=${symbols}`)
        .then(response => response.json())
        .then(data => {
            const resultDiv = document.getElementById('result');
            if (data.error) {
                resultDiv.innerHTML = `<p>Error: ${data.error}</p>`;
            } else {
                let resultHtml = `<h3>Summary:</h3><p>${data.summary}</p>`;
                resultDiv.innerHTML = resultHtml;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert("An error occurred. Please try again.");
        });
}
