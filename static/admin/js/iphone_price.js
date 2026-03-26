// Auto-calculate iPhone price based on storage size
document.addEventListener('DOMContentLoaded', function() {
    const storageSelect = document.getElementById('id_storage');
    const priceInput = document.getElementById('id_price');
    
    if (storageSelect && priceInput) {
        // Storage price mapping (base price + increments)
        const STORAGE_PRICES = {
            '32GB': 4500,   // Base price
            '64GB': 5000,   // +500
            '128GB': 5500,  // +1000
            '256GB': 6000,  // +1500
            '512GB': 6500,  // +2000
            '1TB': 7000,    // +2500
            '2TB': 7500     // +3000
        };
        
        function updatePrice() {
            const selectedStorage = storageSelect.value;
            if (selectedStorage && STORAGE_PRICES[selectedStorage]) {
                priceInput.value = STORAGE_PRICES[selectedStorage];
            }
        }
        
        // Update price when storage changes
        storageSelect.addEventListener('change', updatePrice);
        
        // Set initial price if storage is already selected
        updatePrice();
        
        // Also update when model changes (in case you want model-specific pricing)
        const modelSelect = document.getElementById('id_iphone_model');
        if (modelSelect) {
            modelSelect.addEventListener('change', updatePrice);
        }
    }
});
