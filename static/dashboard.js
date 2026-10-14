let currentPage = 1;
const limit = 25

async function fetchAlerts() {
    try {
        const minVal = document.getElementById('min-amount').value;
        const maxVal = document.getElementById('max-amount').value;
        const params = new URLSearchParams();
        params.append('page', currentPage);
        params.append('limit', limit);
        if (minVal && maxVal){
            params.append('min_filter', minVal);
            params.append('max_filter', maxVal);
        }

        const finalUrl = `/api/alerts?${params.toString()}`;
        const response = await fetch(finalUrl);
        const alerts = await response.json();

        const myButton = document.getElementById('next-btn');

        if (alerts.length < limit){
            myButton.disabled = true;
        }
        else{
            myButton.disabled = false;
        }

        
        const alertBox = document.getElementById('alert-box');

        alertBox.innerHTML = ''; 
        document.getElementById('page-indicator').innerText = `Page ${currentPage}`;
        
        alerts.forEach(alert => {
            const row = document.createElement('tr');
            
            row.innerHTML = `
                <td class="text-start">${alert.user_id}</td>
                <td class="text-end">$${alert.amount.toFixed(2)}</td>
                <td class="text-end neon-threat">${alert.flag_type}</td>
                <td class="text-end">${alert.timestamp}</td>
                <td><button onclick="deleteAlert(${alert.id})">Delete</button></td>
            `;
            
            alertBox.appendChild(row);
        });
    } catch (error) {
        console.error("Error fetching alerts:", error);
    }
}

  
async function deleteAlert(id) { 
    const response = await fetch(`/api/delete/${id}`, { method: 'DELETE' });
    fetchAlerts();
 }


 function nextPage() {
    currentPage++;
    fetchAlerts();
 }


 function prevPage() {
    if (currentPage > 1) {
        currentPage--;
        fetchAlerts();

    }
    else {
        fetchAlerts();
    }
 }


 function applyFilter() {
    currentPage = 1; 
    fetchAlerts();   
}

fetchAlerts();
  