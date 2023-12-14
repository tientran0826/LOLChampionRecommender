 // JavaScript code goes here
        // Sample champion data with both icon and splash art URLs

        let champions = [];

        // Function to fetch champion data from the server
        function fetchChampionData() {
            fetch('/get_champion_data')
                .then(response => response.json())
                .then(data => {
                    champions = data;
                    populateModal(); // Call this function to populate the modal with the fetched data
                })
                .catch(error => {
                    console.error('Error fetching champion data:', error);
                });
        }

        // Call the fetchChampionData function to fetch data when the page loads
        fetchChampionData();

        const roleIcons = [
            '../static/roles/TOP.png', // Path to the top role icon
            '../static/roles/JUNGLE.png', // Path to the jungle role icon
            '../static/roles/MIDDLE.png', // Path to the mid role icon
            '../static/roles/BOTTOM.png', // Path to the bot role icon
            '../static/roles/UTILITY.png' // Path to the support role icon
        ];

        // Function to reset the selection of a champion box
        function resetChampionBox(box) {
            box.style.backgroundImage = '';
            box.classList.remove('selected');
            // Remove the cancel pick icon if it exists
            const cancelIcon = box.querySelector('.cancel-pick-icon');
            if (cancelIcon) {
                box.removeChild(cancelIcon);
            }
        }

        // Function to create champion boxes for a team
        function createChampionBoxes(teamId) {
            const teamContainer = document.getElementById(teamId);
            const roleNames = ['TOP', 'JUNGLE', 'MIDDLE', 'BOTTOM', 'UTILITY'];

            for (let i = 0; i < roleNames.length; i++) {
                const roleName = roleNames[i];
                const box = document.createElement('div');
                box.className = 'champion-box';
                
                // Create an image element for the role icon
                const roleIcon = document.createElement('img');
                roleIcon.className = 'role-icon';
                roleIcon.alt = roleName; // Set the alt attribute to the role name

                // Set the src attribute of the role icon based on the role name
                roleIcon.src = roleIcons[i];

                // Append the role icon to the box
                box.appendChild(roleIcon);
                
                // Add the click event to the box
                box.onclick = function() {
                    if (this.classList.contains('selected')) {
                        // Box is already selected, remove the champion
                        resetChampionBox(this);
                
                        // Check if the '.champion-name' element exists before trying to access its textContent
                        const championNameElement = this.querySelector('.champion-name');
                        if (championNameElement) {
                            const championName = championNameElement.textContent;
                            delete championToBoxMapping[championName]; // Remove from mapping
                        }
                    } else {
                        // No champion selected yet, show the modal to select
                        selectedBox = this; // Store the clicked box reference
                        showModal();
                    }
                };
                // Append the box to the team container
                teamContainer.appendChild(box);
            }
        }

        // Call createChampionBoxes function for each team
        createChampionBoxes('team1');
        createChampionBoxes('team2');

        // Function to show the modal
        function showModal() {
            document.getElementById('championModal').style.display = 'block';
        }

        // Function to close the modal
        function closeModal() {
            document.getElementById('championModal').style.display = 'none';
        }
        function cancelIconClickHandler(event) {
            event.stopPropagation(); // Prevent the box click event from firing
            const box = event.currentTarget.closest('.champion-box');
            resetChampionBox(box);
        }

        let championToBoxMapping = {}; // Maps champion names to their boxes

        function selectChampion(champion) {
            const championName = champion.ChampionName;
            const selectedBoxBackground = `url(${champion.LoadingImageURL})`;
        
            // Check if this champion is already selected in another box and reset if necessary
            if (championToBoxMapping[championName]) {
                resetChampionBox(championToBoxMapping[championName]);
            }
        
            // Update the current box with the new champion background image
            selectedBox.style.backgroundImage = selectedBoxBackground;
            selectedBox.classList.add('selected');
        
            // Store the champion's name in a data attribute on the box
            selectedBox.setAttribute('data-champion-name', championName);
        
            // Create the cancel icon element
            const cancelIcon = document.createElement('i');
            cancelIcon.classList.add('fas', 'fa-times', 'cancel-pick-icon');
            
            // Define the cancel icon click handler with proper closure
            const cancelIconClickHandler = function(event) {
                event.stopPropagation(); // Prevent the box click event from firing
                resetChampionBox(selectedBox);
            };
        
            // Attach the click event listener to the cancel icon
            cancelIcon.addEventListener('click', cancelIconClickHandler);
        
            // Append the cancel icon to the selected box
            selectedBox.appendChild(cancelIcon);
        
            // Update the mapping
            championToBoxMapping[championName] = selectedBox;
        }
        function resetChampionBox(box) {
            // Clear the background image and selected state
            box.style.backgroundImage = '';
            box.classList.remove('selected');
        
            // Remove the cancel pick icon if it exists
            const cancelIcon = box.querySelector('.cancel-pick-icon');
            if (cancelIcon) {
                cancelIcon.removeEventListener('click', cancelIconClickHandler);
                box.removeChild(cancelIcon);
            }
        
            // Remove the data attribute storing the champion's name
            const championName = box.getAttribute('data-champion-name');
            box.removeAttribute('data-champion-name');
        
            // Remove the champion from the mapping
            if (championName && championToBoxMapping[championName] === box) {
                delete championToBoxMapping[championName];
            }
        }
        
        function populateModal() {
            const grid = document.querySelector('.champion-grid');
            grid.innerHTML = ''; // Clear the grid first
        
            const championItemsHtml = champions.map(champion => {
                return `
                    <div class="champion-item" onclick="handleChampionClick('${champion.ChampionName}')">
                        <div class="overlay"></div>
                        <img src="${champion.IconURL}" alt="${champion.ChampionName}" class="champion-icon">
                        <div class="champion-name">${champion.ChampionName}</div>
                    </div>
                `;
            }).join('');
        
            grid.innerHTML = championItemsHtml;
        
            // Add the 'scrollable' class to the modal content
            const modalContent = document.querySelector('.modal-content');
            modalContent.classList.add('scrollable');
        }

        function handleChampionClick(championName) {
            const champion = champions.find(c => c.ChampionName === championName);
            if (champion) {
                selectChampion(champion);
                closeModal();
            }
        }

        // Filter champions based on the search input
        document.getElementById('championSearch').addEventListener('input', function(e) {
            const searchValue = e.target.value.toLowerCase();
            const championItems = document.querySelectorAll('.champion-item');
            championItems.forEach(item => {
                const name = item.querySelector('.champion-name').textContent.toLowerCase();
                if (name.includes(searchValue)) {
                    item.style.display = 'block';
                } else {
                    item.style.display = 'none';
                }
            });
        });

        // Event listener for closing the modal when clicking on the '×' button
        document.querySelector('.close').addEventListener('click', function() {
            closeModal();
        });

        // Event listener for closing the modal when clicking outside of it
        window.addEventListener('click', function(event) {
            const modal = document.getElementById('championModal');
            if (event.target === modal) {
                closeModal();
            }
        });

             // Event listener for the "Clear All" button
             document.getElementById('clearButton').addEventListener('click', function() {
            clearAllChampions();
        });
        function clearAllChampions() {
            // Clear each champion box and mapping
            showLoading();
            document.querySelectorAll('.champion-box').forEach(box => {
                resetChampionBox(box);
            });
        
            // Reset the mapping
            championToBoxMapping = {}; // This will now work without an error
        
            // Clear the recommendation results
            const statsContainer = document.getElementById('stats-container');
            if (statsContainer) {
                statsContainer.innerHTML = '';
                console.log('Recommendation results cleared.');
            } else {
                console.log('stats-container element not found.');
            }
            setTimeout(hideLoading, 200);

            closeModal();
        }
        // Initial population of the modal with champions
        populateModal();
        document.querySelectorAll('.champion-box').forEach(box => {
            box.addEventListener('click', function() {
                // Remove 'clicked' class from all boxes
                document.querySelectorAll('.champion-box').forEach(b => b.classList.remove('clicked'));

                // Add 'clicked' class to the clicked box
                this.classList.add('clicked');
        });
    });
    // Function to send champion data to Flask
// Function to collect selected champions and roles
function collectSelectedChampions() {
    const team1Champions = [];
    const team2Champions = [];

    for (const [championName, box] of Object.entries(championToBoxMapping)) {
        const roleName = box.querySelector('.role-icon').alt;
        if (team1Champions.length < 5 && box.parentElement.id === 'team1') {
            team1Champions.push([championName, roleName]);
        } else if (team2Champions.length < 5 && box.parentElement.id === 'team2') {
            team2Champions.push([championName, roleName]);
        }
    }

    return {
        team1: team1Champions,
        team2: team2Champions,
    };
}
// Function to show the notification
function showNotification(message) {
    const notification = document.getElementById('notification');
    notification.textContent = message;
    notification.style.display = 'block';

    // Hide the notification after 5 seconds (adjust the time as needed)
    setTimeout(function () {
        notification.style.display = 'none';
    }, 5000);
}
function fetchChampionIconsAndDisplayResults(modelData) {
    fetch('/get_champion_data')
      .then(response => response.json())
      .then(championData => {
        // Create a mapping of champion names to icon URLs
        const iconMapping = championData.reduce((map, champ) => {
          map[champ.ChampionName] = champ.IconURL;
          return map;
        }, {});
  
        // Now display the results with icons
        displayResults(modelData, iconMapping);
      })
      .catch(error => {
        console.error('Error fetching champion icons:', error);
      });
  }
  
// Function to send selected champion data to Flask
function sendChampionDataToFlask() {
    
    const championData = collectSelectedChampions();
    const team1ChampionNames = championData.team1.map(([championName, _]) => championName);

    if (!team1ChampionNames.includes("PredictRole")) {
        // "Role dự đoán" is not in team1, raise an error notification
        showNotification("Vui lòng lựa chọn Role cần gợi ý (PredictRole)", true);
        return;
    }

    if (championData.team2.length === 0) {
        // Team 2 is empty, raise an error notification
        showNotification("Không được để trống team địch!", true);
        return;
    }
    showLoading();
    fetch('/send_champion_data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(championData),
    })
    .then(response => response.json())
    .then(data => {
        fetchChampionIconsAndDisplayResults(data);
        setTimeout(hideLoading, 200);

        console.log('Champion data sent successfully:', data);
        // Handle the server response if needed
        showNotification('Gửi dữ liệu đến Server thành công', false); // Success notification
    })
    .catch(error => {
        hideLoading();
        console.error('Error sending champion data:', error);
        showNotification('Error sending champion data', true); // Error notification
    });
}
function displayResults(data, iconMapping) {
    const statsContainer = document.getElementById('stats-container');
    if (!statsContainer) {
      console.error('Stats container not found');
      return;
    }
  
    statsContainer.innerHTML = ''; // Clear existing content
  
    const scoreTypes = {
      'Synergy Score': 'Lối chơi phối hợp',
      'Counter Score': 'Lối chơi khắc chế',
      'Harmonic Score': 'Lối chơi cân bằng'
    };
  
    Object.entries(scoreTypes).forEach(([scoreType, title]) => {
      // Get the top 10 champions based on the scoreType
      const championsWithScore = data.modelResult
        .filter(champ => champ[scoreType] > 0)
        .sort((a, b) => b[scoreType] - a[scoreType])
        .slice(0, 4); // Only take the top 10
  
      let championsHTML = championsWithScore.length > 0
        ? championsWithScore.map(champ => championHTML(champ, scoreType, champ[scoreType], iconMapping)).join('')
        : `<div class="no-data-message fade-in">Chưa đủ dữ liệu để gợi ý</div>`;
  
      const boxHTML = `
        <div class="champion-score-box fade-in">
          <h3 class="champion-score-header">${title}</h3>
          <div class="champion-score-items">${championsHTML}</div>
        </div>
      `;
  
      statsContainer.insertAdjacentHTML('beforeend', boxHTML);
    });
  }
  
  function championHTML(champion, scoreType, scoreValue, iconMapping) {
    // Assumes `iconMapping` is an object where the key is the champion name and the value is the icon URL
    const iconUrl = iconMapping[champion.Champion]; // Use the mapping to get the icon URL

    return `
            <div class="champion-item fade-in">
                <img src="${iconUrl}" alt="${champion.Champion}" class="champion-icon">
                <div class="champion-name">${champion.Champion}</div>
                <div class="champion-score">${scoreType}: ${scoreValue.toFixed(2)}</div>
            </div>
        `;
  }
// Modify the "Gợi ý tướng" button click event to send the selected champion data
document.getElementById('suggestChampionButton').addEventListener('click', function() {
    sendChampionDataToFlask();
});
function showNotification(message, isError) {
    const notification = document.getElementById('notification');
    const notificationText = document.getElementById('notification-text');

    if (notification && notificationText) {
        notificationText.textContent = message;

        if (isError) {
            notification.style.backgroundColor = 'red';
        } else {
            notification.style.backgroundColor = 'green';
        }

        notification.style.display = 'block';

        setTimeout(() => {
            notification.style.display = 'none';
        }, 3000); // Hide the notification after 3 seconds (adjust as needed)
    } else {
        console.error('Notification elements not found in HTML.');
    }
}

function showLoading() {
    const loadingOverlay = document.getElementById('loadingOverlay');
    if (loadingOverlay) {
      loadingOverlay.classList.remove('hidden');
    }
  }
  
  function hideLoading() {
    const loadingOverlay = document.getElementById('loadingOverlay');
    if (loadingOverlay) {
      loadingOverlay.classList.add('hidden');
    }
  }

  function createElementWithData(item) {
    const element = document.createElement('div');
    element.classList.add('fade-in'); // Apply the fade-in animation class
    // Set up the rest of your element here
    return element;
  }
  
  // Then, when you load your data and create your elements:
  data.forEach(item => {
    const element = createElementWithData(item);
    document.body.appendChild(element);
  });