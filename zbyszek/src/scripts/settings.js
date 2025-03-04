async function LoginViaSteam() {
    try {
        await ipcRenderer.invoke('LoginViaSteam');
        console.log("JESTEM");
    } catch (error) {
        console.error('Błąd podczas logowania przez Steam:', error);
    }
    GetAccount();
}

async function LoginViaEpic() {
    try {
        await ipcRenderer.invoke('LoginViaEpic');
        console.log("JESTEM");
    } catch (error) {
        console.error('Błąd podczas logowania przez EPIC:', error);
    }
    GetAccount();
}

async function LoginViaEA() {
    try {
        await ipcRenderer.invoke('LoginViaEA');
        console.log("JESTEM");
    } catch (error) {
        console.error('Błąd podczas logowania przez EA:', error);
    }
    GetAccount();
}

function LoginViaBattleNet() {}

function SyncGames() {
    fetch("http://localhost:8090/api/sync", {
        method: "GET",
        headers: {
            "Content-Type": "application/json"
        }
    }).then(response => {
        if (response.ok) {
            console.log("Synchronizacja zakończona.");
        }
    });
}

function GetAccount() {
    fetch('http://localhost:8090/api/accounts')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (!data || !data.accounts || !Array.isArray(data.accounts)) {
                console.error("Błąd: Oczekiwano tablicy w 'data.accounts', ale otrzymano:", data);
                return;
            }

            const accountList = data.accounts;
            const steamAcc = document.getElementById('steam-accounts');
            const epicAcc = document.getElementById('epic-accounts');
            const eaAcc = document.getElementById('ea-accounts');
            const savedEntries = document.getElementById('saved-entries');

            [steamAcc, epicAcc, eaAcc, savedEntries].forEach(el => {
                if (el) el.innerHTML = '';
            });

            accountList.forEach(account => {
                if (!account || !account.platform || !account.accountName) {
                    console.warn("Pominięto błędne konto:", account);
                    return;
                }

                const li = document.createElement('li');
                li.className = 'account-item';
                li.style.display = 'flex';
                li.style.alignItems = 'center';
                li.style.gap = '5px';
                li.style.padding = '5px 0';

                const nameSpan = document.createElement('span');
                nameSpan.textContent = account.accountName;
                nameSpan.style.width = '150px';


                if (account.platform === 'Steam') {
                    const input = document.createElement('input');
                    input.className = 'account-input';
                    if (account.steamAPI != null){
                        input.value = account.steamAPI;
                    }else {
                        input.placeholder = 'Enter API Key';
                    }
                    input.style.flex = '1';
                    input.style.padding = '5px';

                    const saveButton = document.createElement('button');
                    saveButton.textContent = 'Save';
                    saveButton.className = 'save-btn';

                    saveButton.onclick = () => {
                        fetch(`http://localhost:8090/api/save/${account.id}/${input.value}`)
                        .then(response => response.json())
                        .then(data => console.log(data))
                        .catch(error => console.error('Error:', error));
                    };

                    const logoutButton = document.createElement('button');
                    logoutButton.textContent = 'X';
                    logoutButton.style.color = 'red';
                    logoutButton.className = 'save-btn';

                    logoutButton.onclick = () => logoutAccount(account.id, li);
                    const LogIn = document.createElement('button');
                    LogIn.textContent = 'Log In';
                    LogIn.className = 'save-btn';
                    LogIn.style.marginLeft = '10px';
                    LogIn.onclick = async () =>{
                        console.log(account.accountid)
                        const response = await fetch(`http://localhost:8090/api/run/steam/?steamid=${account.accountid}`)
                    };
                    li.appendChild(logoutButton);
                    li.appendChild(nameSpan);
                    li.appendChild(input);
                    li.appendChild(saveButton);
                    li.appendChild(LogIn);
                } else {

                    const logoutButton = document.createElement('button');
                    logoutButton.textContent = 'X';
                    logoutButton.style.color = 'red';
                    logoutButton.className = 'save-btn';
                    logoutButton.style.marginLeft = 'auto';


                    logoutButton.onclick = () => logoutAccount(account.id, li);
                    li.appendChild(logoutButton);
                    li.appendChild(nameSpan);
                }

                switch (account.platform) {
                    case 'Steam':
                        steamAcc?.appendChild(li);
                        break;
                    case 'EPIC':
                        epicAcc?.appendChild(li);
                        break;
                    case 'EA':
                        eaAcc?.appendChild(li);
                        break;
                }
            });
        })
        .catch(error => console.error('Błąd:', error));
}


function logoutAccount(accountId, liElement) {
    fetch(`http://localhost:8090/logout/${accountId}`, { method: 'GET' })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok ' + response.statusText);
            }
            console.log(`Account with id ${accountId} logged out successfully`);
            liElement.remove();
        })
        .catch(error => {
            console.error('There was a problem with the fetch operation:', error);
        });
}

window.onload = GetAccount;
async function findids(){
    showLoader();
    await fetch("http://localhost:8090/find")
    location.reload();
    hideLoader()
}