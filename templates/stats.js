// Fonction pour créer un camembert
function createPieChart(chartId, labels, values, colors) {
    const ctx = document.getElementById(chartId).getContext("2d");
    new Chart(ctx, {
        type: "pie",
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: colors,
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
        },
    });
}

// Récupérer les données passées dans le template
document.addEventListener('DOMContentLoaded', function() {
    // Les données sont injectées dans le HTML via Flask
    const chartData = JSON.parse('{{ chart_data | tojson | safe }}');
    
    // Camembert du début
    createPieChart(
        'pieChart1',
        chartData.debut.labels,
        chartData.debut.values,
        ['#FF6384', '#36A2EB', '#FFCE56']
    );

    // Camembert de la fin
    createPieChart(
        'pieChart2',
        chartData.fin.labels,
        chartData.fin.values,
        ['#FF6384', '#36A2EB', '#FFCE56']
    );
});