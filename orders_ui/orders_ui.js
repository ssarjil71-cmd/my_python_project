// Orders UI JavaScript - Table-wise QR Ordering System

// Global variables
let tables = [];
let currentOrder = [];
let orders = [];

// Initialize tables with proper numbering
function initializeTables() {
    tables = [
        { number: 1, qrNumber: 'QR-001' },
        { number: 2, qrNumber: 'QR-002' },
        { number: 3, qrNumber: 'QR-003' },
        { number: 4, qrNumber: 'QR-004' },
        { number: 5, qrNumber: 'QR-005' },
        { number: 6, qrNumber: 'QR-006' }
    ];
    
    renderTables();
}

// Render tables grid
function renderTables() {
    const tablesGrid = document.getElementById('tables-grid');
    if (!tablesGrid) return;
    
    tablesGrid.innerHTML = '';
    
    tables.forEach(table => {
        const tableCard = document.createElement('div');
        tableCard.className = 'table-card';
        tableCard.innerHTML = `
            <div class="table-number">Table ${table.number}</div>
            <div class="qr-placeholder" onclick="simulateQRScan(${table.number}, '${table.qrNumber}')">
                <i class="fas fa-qrcode" style="font-size: 3rem; color: #cbd5e0;"></i>
            </div>
            <div class="qr-number">${table.qrNumber}</div>
            <button class="download-qr-btn" onclick="downloadQR('${table.qrNumber}')">
                <i class="fas fa-download"></i> Download QR
            </button>
        `;
        tablesGrid.appendChild(tableCard);
    });
}

// Add new table with automatic numbering
function addNewTable() {
    const nextTableNumber = tables.length + 1;
    const nextQRNumber = `QR-${String(nextTableNumber).padStart(3, '0')}`;
    
    tables.push({
        number: nextTableNumber,
        qrNumber: nextQRNumber
    });
    
    renderTables();
    
    // Show success message
    alert(`New table added!\nTable ${nextTableNumber} with ${nextQRNumber}`);
}

// Simulate QR code scan
function simulateQRScan(tableNumber, qrNumber) {
    localStorage.setItem('selectedTable', tableNumber);
    localStorage.setItem('selectedQR', qrNumber);
    window.location.href = 'guest_menu.html';
}

// Download QR (UI simulation)
function downloadQR(qrNumber) {
    alert(`Downloading ${qrNumber} QR Code...\n(This is a UI simulation)`);
}

// Initialize guest menu
function initializeGuestMenu() {
    const tableNumber = localStorage.getItem('selectedTable') || '1';
    const qrNumber = localStorage.getItem('selectedQR') || 'QR-001';
    
    const tableInfo = document.querySelector('.table-info');
    if (tableInfo) {
        tableInfo.innerHTML = `
            <span class="table-badge">Table ${tableNumber}</span>
            <span class="qr-badge">${qrNumber}</span>
        `;
    }
    
    updateOrderButton();
}

// Add item to order
function addToOrder(itemName, price) {
    const existingItem = currentOrder.find(item => item.name === itemName);
    
    if (existingItem) {
        existingItem.quantity += 1;
    } else {
        currentOrder.push({
            name: itemName,
            price: price,
            quantity: 1
        });
    }
    
    updateOrderButton();
}

// Update floating order button
function updateOrderButton() {
    const orderBtn = document.getElementById('order-btn');
    if (orderBtn) {
        const totalItems = currentOrder.reduce((sum, item) => sum + item.quantity, 0);
        const totalPrice = currentOrder.reduce((sum, item) => sum + (item.price * item.quantity), 0);
        
        if (totalItems > 0) {
            orderBtn.textContent = `Place Order (${totalItems} items - $${totalPrice.toFixed(2)})`;
            orderBtn.style.display = 'block';
        } else {
            orderBtn.style.display = 'none';
        }
    }
}

// Place order
function placeOrder() {
    if (currentOrder.length === 0) {
        alert('Please add items to your order first!');
        return;
    }
    
    const tableNumber = localStorage.getItem('selectedTable') || '1';
    const qrNumber = localStorage.getItem('selectedQR') || 'QR-001';
    
    // Create order object
    const order = {
        tableNumber: parseInt(tableNumber),
        qrNumber: qrNumber,
        items: currentOrder.map(item => `${item.name} (x${item.quantity})`).join(', '),
        totalAmount: currentOrder.reduce((sum, item) => sum + (item.price * item.quantity), 0),
        orderTime: new Date().toLocaleString(),
        status: 'New'
    };
    
    // Store order
    let existingOrders = JSON.parse(localStorage.getItem('qrOrders') || '[]');
    existingOrders.unshift(order);
    localStorage.setItem('qrOrders', JSON.stringify(existingOrders));
    
    // Show success message
    alert(`Order placed successfully!\n\nTable: ${tableNumber}\nQR: ${qrNumber}\nTotal: $${order.totalAmount.toFixed(2)}\n\nRedirecting to orders dashboard...`);
    
    // Clear current order
    currentOrder = [];
    
    // Redirect to orders dashboard
    window.location.href = 'orders_dashboard.html';
}

// Load orders data for dashboard
function loadOrdersData() {
    const tableBody = document.getElementById('orders-table-body');
    if (!tableBody) return;
    
    // Get orders from localStorage
    const storedOrders = JSON.parse(localStorage.getItem('qrOrders') || '[]');
    
    // Sample orders for demonstration
    const sampleOrders = [
        {
            tableNumber: 2,
            qrNumber: 'QR-002',
            items: 'Chicken Curry, Rice, Naan',
            totalAmount: 24.50,
            orderTime: '15 mins ago',
            status: 'New'
        },
        {
            tableNumber: 5,
            qrNumber: 'QR-005',
            items: 'Pizza Margherita, Coke',
            totalAmount: 18.75,
            orderTime: '22 mins ago',
            status: 'New'
        },
        {
            tableNumber: 1,
            qrNumber: 'QR-001',
            items: 'Burger, Fries, Milkshake',
            totalAmount: 22.25,
            orderTime: '28 mins ago',
            status: 'New'
        }
    ];
    
    // Combine stored and sample orders
    const allOrders = [...storedOrders, ...sampleOrders];
    
    tableBody.innerHTML = '';
    
    if (allOrders.length === 0) {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td colspan="6" style="text-align: center; padding: 3rem; color: #718096;">
                <i class="fas fa-inbox" style="font-size: 2rem; margin-bottom: 1rem; opacity: 0.5;"></i><br>
                No orders received yet
            </td>
        `;
        tableBody.appendChild(row);
        return;
    }
    
    allOrders.forEach(order => {
        const row = document.createElement('tr');
        row.style.borderBottom = '1px solid #f1f5f9';
        row.onmouseover = () => row.style.background = '#f8fafc';
        row.onmouseout = () => row.style.background = 'white';
        
        row.innerHTML = `
            <td style="padding: 1rem;">
                <span class="table-number-badge">Table ${order.tableNumber}</span>
            </td>
            <td style="padding: 1rem;">
                <span class="qr-number-badge">${order.qrNumber}</span>
            </td>
            <td style="padding: 1rem;">${order.items}</td>
            <td style="padding: 1rem; font-weight: 600;">$${order.totalAmount.toFixed(2)}</td>
            <td style="padding: 1rem; color: #718096;">${order.orderTime}</td>
            <td style="padding: 1rem;">
                <span class="status-${order.status.toLowerCase()}">${order.status}</span>
            </td>
        `;
        tableBody.appendChild(row);
    });
}