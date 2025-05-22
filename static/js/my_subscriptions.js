document.addEventListener('DOMContentLoaded', function() {
    const categoryFilter = document.getElementById('categoryFilter');
    const sortSelect = document.getElementById('sortSelect');
    const subscriptionsTable = document.getElementById('subscriptionsTable');
    const tableBody = subscriptionsTable.querySelector('tbody');
    const originalRows = Array.from(tableBody.querySelectorAll('tr'));
    
    function filterAndSortSubscriptions() {
        const selectedCategory = categoryFilter.value;
        const sortOption = sortSelect.value;
        
        // Reset to original rows if no category is selected
        if (!selectedCategory) {
            tableBody.innerHTML = '';
            originalRows.forEach(row => tableBody.appendChild(row));
        }
        
        // Filter rows by category
        const filteredRows = originalRows.filter(row => {
            const categoryCell = row.querySelector('td:nth-child(2) .badge');
            if (!selectedCategory) return true;
            return categoryCell.textContent.trim() === selectedCategory;
        });
        
        // Sort filtered rows
        const sortedRows = filteredRows.sort((a, b) => {
            switch(sortOption) {
                case 'name_asc':
                    return a.cells[0].textContent.localeCompare(b.cells[0].textContent);
                case 'name_desc':
                    return b.cells[0].textContent.localeCompare(a.cells[0].textContent);
                case 'cost_asc':
                    return parseFloat(a.cells[2].textContent.replace(/[^\d.]/g, '')) - 
                           parseFloat(b.cells[2].textContent.replace(/[^\d.]/g, ''));
                case 'cost_desc':
                    return parseFloat(b.cells[2].textContent.replace(/[^\d.]/g, '')) - 
                           parseFloat(a.cells[2].textContent.replace(/[^\d.]/g, ''));
                case 'date_asc':
                    return new Date(a.cells[3].textContent) - new Date(b.cells[3].textContent);
                case 'date_desc':
                    return new Date(b.cells[3].textContent) - new Date(a.cells[3].textContent);
                default:
                    return 0;
            }
        });
        
        // Clear the table body
        tableBody.innerHTML = '';
        
        // Reinsert sorted rows
        sortedRows.forEach(row => {
            tableBody.appendChild(row);
        });
    }
    
    categoryFilter.addEventListener('change', filterAndSortSubscriptions);
    sortSelect.addEventListener('change', filterAndSortSubscriptions);
});