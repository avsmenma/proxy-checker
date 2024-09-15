document.getElementById('proxy-form').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const proxyList = document.getElementById('proxy-list').value.trim().split('\n');

    // Tampilkan loading spinner dan progress bar
    document.querySelector('.loading-spinner').style.display = 'block';
    const progressBar = document.querySelector('.progress-bar');
    progressBar.style.display = 'block';
    const progressText = document.getElementById('progress-text');

    fetch('/check_proxy', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ proxies: proxyList })
    })
    .then(response => response.json())
    .then(data => {
        const tableBody = document.querySelector('#result-table tbody');
        tableBody.innerHTML = '';

        data.forEach(result => {
            const row = `<tr>
                <td>${result.ip}:${result.port}</td>
                <td>${result.login || '-'}</td>
                <td>${result.password || '-'}</td>
                <td>${result.type.toUpperCase()}</td>
                <td class="${result.status === 'alive' ? 'status-success' : 'status-fail'}">${result.status === 'alive' ? 'Alive' : 'Dead'}</td>
                <td>${result.response_time || '-'}</td>
            </tr>`;
            tableBody.innerHTML += row;

            // Update progress bar
            progressBar.querySelector('span').style.width = `${result.progress}%`;
            progressText.textContent = `${Math.round(result.progress)}%`;
        });

        // Sembunyikan loading spinner dan progress bar setelah pengecekan selesai
        document.querySelector('.loading-spinner').style.display = 'none';
        progressBar.style.display = 'none';
    })
    .catch(error => {
        console.error('Error:', error);
        
        // Sembunyikan loading spinner dan progress bar jika terjadi kesalahan
        document.querySelector('.loading-spinner').style.display = 'none';
        progressBar.style.display = 'none';
    });
});
