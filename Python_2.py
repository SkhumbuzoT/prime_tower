<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PrimeTower Fleet Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        primary: '#000000', // Jet Black
                        teal: '#008080', // Teal
                        gold: '#D4AF37', // Gold
                        navy: '#0A1F44', // Navy Blue
                        white: '#FFFFFF', // White
                        lightgray: '#F8F9FA', // Light Gray
                        red: '#d32f2f', // Red
                        orange: '#ffa726', // Orange
                        greenteal: '#26a69a', // Green Teal
                        purple: '#9c27b0', // Purple
                    }
                }
            }
        }
    </script>
    <style>
        /* Custom scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
        }
        ::-webkit-scrollbar-track {
            background: #000000;
        }
        ::-webkit-scrollbar-thumb {
            background: #008080;
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #006666;
        }
        
        /* Chart styles */
        .chart-container {
            background-color: #0A1F44;
            border-radius: 0.5rem;
            padding: 1rem;
            border: 1px solid #008080;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        }
        
        /* Login box animation */
        .login-box {
            transition: all 0.3s ease;
        }
        .login-box:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
        }
        
        /* Sidebar menu item hover */
        .menu-item:hover {
            background-color: rgba(0, 128, 128, 0.2);
        }
        
        /* Active menu item */
        .menu-item.active {
            background-color: #008080;
            color: white;
        }
    </style>
</head>
<body class="bg-primary text-white font-sans">
    <!-- Login Screen -->
    <div id="login-screen" class="fixed inset-0 flex items-center justify-center bg-black bg-opacity-90 z-50">
        <div class="login-box bg-navy p-8 rounded-lg border border-teal w-full max-w-md">
            <div class="text-center mb-6">
                <i class="fas fa-lock text-teal text-3xl mb-2"></i>
                <h2 class="text-teal text-2xl font-bold">🔐 Prime Tower Login</h2>
            </div>
            <div class="space-y-4">
                <div>
                    <label for="username" class="block text-sm font-medium mb-1">Username</label>
                    <input type="text" id="username" class="w-full px-3 py-2 bg-navy border border-teal rounded-md focus:outline-none focus:ring-1 focus:ring-teal">
                </div>
                <div>
                    <label for="password" class="block text-sm font-medium mb-1">Password</label>
                    <input type="password" id="password" class="w-full px-3 py-2 bg-navy border border-teal rounded-md focus:outline-none focus:ring-1 focus:ring-teal">
                </div>
                <button onclick="login()" class="w-full bg-teal text-white py-2 px-4 rounded-md hover:bg-opacity-90 transition duration-200">Login</button>
            </div>
            <p id="login-error" class="text-red-500 text-sm mt-2 hidden">Invalid credentials</p>
        </div>
    </div>

    <!-- Main Dashboard -->
    <div id="dashboard" class="hidden min-h-screen flex">
        <!-- Sidebar -->
        <div class="w-64 bg-navy border-r border-teal flex flex-col">
            <div class="p-4 border-b border-teal">
                <div class="flex items-center justify-center mb-4">
                    <img src="https://via.placeholder.com/100" alt="Prime Tower Logo" class="w-16 h-16 rounded-full">
                </div>
                <div class="text-center">
                    <h4 class="text-teal font-semibold">Welcome, <span id="username-display">Admin</span></h4>
                </div>
            </div>
            
            <!-- Navigation Menu -->
            <div class="flex-1 overflow-y-auto py-4">
                <div class="space-y-1 px-2">
                    <a href="#" class="menu-item active flex items-center px-4 py-2 text-sm rounded-md" onclick="switchTab('home')">
                        <i class="fas fa-home mr-3 text-gold"></i>
                        Home
                    </a>
                    <a href="#" class="menu-item flex items-center px-4 py-2 text-sm rounded-md" onclick="switchTab('cost')">
                        <i class="fas fa-cash-stack mr-3 text-gold"></i>
                        Cost & Profitability
                    </a>
                    <a href="#" class="menu-item flex items-center px-4 py-2 text-sm rounded-md" onclick="switchTab('operations')">
                        <i class="fas fa-tachometer-alt mr-3 text-gold"></i>
                        Daily Operations
                    </a>
                    <a href="#" class="menu-item flex items-center px-4 py-2 text-sm rounded-md" onclick="switchTab('fuel')">
                        <i class="fas fa-gas-pump mr-3 text-gold"></i>
                        Fuel Efficiency
                    </a>
                    <a href="#" class="menu-item flex items-center px-4 py-2 text-sm rounded-md" onclick="switchTab('maintenance')">
                        <i class="fas fa-tools mr-3 text-gold"></i>
                        Maintenance
                    </a>
                    <a href="#" class="menu-item flex items-center px-4 py-2 text-sm rounded-md" onclick="switchTab('insights')">
                        <i class="fas fa-lightbulb mr-3 text-gold"></i>
                        Insights
                    </a>
                </div>
            </div>
            
            <!-- Filters -->
            <div class="p-4 border-t border-teal">
                <div class="mb-4">
                    <label class="block text-sm font-medium mb-1">Select Month</label>
                    <select class="w-full px-3 py-2 bg-navy border border-teal rounded-md focus:outline-none focus:ring-1 focus:ring-teal">
                        <option>January 2023</option>
                        <option>February 2023</option>
                        <option selected>March 2023</option>
                    </select>
                </div>
                <div class="mb-4">
                    <label class="block text-sm font-medium mb-1">Filter by Truck</label>
                    <select class="w-full px-3 py-2 bg-navy border border-teal rounded-md focus:outline-none focus:ring-1 focus:ring-teal">
                        <option selected>All</option>
                        <option>Truck 1</option>
                        <option>Truck 2</option>
                    </select>
                </div>
                <div class="mb-4">
                    <label class="block text-sm font-medium mb-1">Filter by Route</label>
                    <select class="w-full px-3 py-2 bg-navy border border-teal rounded-md focus:outline-none focus:ring-1 focus:ring-teal">
                        <option selected>All</option>
                        <option>Route A</option>
                        <option>Route B</option>
                    </select>
                </div>
                <button onclick="logout()" class="w-full bg-teal text-white py-2 px-4 rounded-md hover:bg-opacity-90 transition duration-200">Logout</button>
            </div>
        </div>
        
        <!-- Main Content -->
        <div class="flex-1 overflow-y-auto">
            <!-- Home Tab -->
            <div id="home-tab" class="p-6">
                <div class="flex items-center mb-6">
                    <h1 class="text-teal text-3xl font-bold mr-2">Prime Tower</h1>
                    <span class="text-gold text-lg mt-1">Clarity. Control. Growth.</span>
                </div>
                
                <div class="mb-8">
                    <h2 class="text-2xl font-bold mb-4">🚀 Welcome to Prime Tower</h2>
                    <p class="mb-6">
                        <strong>Prime Tower</strong> is your real-time dashboard to track trips, costs, claims, and profits — 
                        all from your Google Sheet or our demo data.
                    </p>
                    
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                        <div class="bg-navy p-6 rounded-lg border border-teal">
                            <h3 class="text-xl font-bold mb-3">1. Try Demo Data</h3>
                            <p class="mb-4">Explore the app with sample data to see how it works</p>
                            <button onclick="useDemoData()" class="w-full bg-teal text-white py-2 px-4 rounded-md hover:bg-opacity-90 transition duration-200">
                                🧪 Try Demo Data
                            </button>
                        </div>
                        <div class="bg-navy p-6 rounded-lg border border-teal">
                            <h3 class="text-xl font-bold mb-3">2. Connect Your Sheet</h3>
                            <p class="mb-4">Use your own data with our Google Sheet template</p>
                            <button onclick="connectSheet()" class="w-full bg-teal text-white py-2 px-4 rounded-md hover:bg-opacity-90 transition duration-200">
                                📊 Connect Google Sheet
                            </button>
                        </div>
                        <div class="bg-navy p-6 rounded-lg border border-teal">
                            <h3 class="text-xl font-bold mb-3">3. View Template</h3>
                            <p class="mb-4">See how to structure your data for Prime Tower</p>
                            <button onclick="viewTemplate()" class="w-full bg-teal text-white py-2 px-4 rounded-md hover:bg-opacity-90 transition duration-200">
                                📄 View Sheet Template
                            </button>
                        </div>
                    </div>
                    
                    <div class="mb-8">
                        <h3 class="text-xl font-bold mb-4">🔑 Key Features</h3>
                        <div class="overflow-x-auto">
                            <table class="min-w-full border-collapse">
                                <thead>
                                    <tr class="border-b border-teal">
                                        <th class="px-4 py-2 text-left">Feature</th>
                                        <th class="px-4 py-2 text-left">Description</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr class="border-b border-teal border-opacity-50">
                                        <td class="px-4 py-2"><strong>Real-time Tracking</strong></td>
                                        <td class="px-4 py-2">Monitor trips, costs, and profits as they happen</td>
                                    </tr>
                                    <tr class="border-b border-teal border-opacity-50">
                                        <td class="px-4 py-2"><strong>Fleet Analytics</strong></td>
                                        <td class="px-4 py-2">Compare performance across trucks and routes</td>
                                    </tr>
                                    <tr class="border-b border-teal border-opacity-50">
                                        <td class="px-4 py-2"><strong>Fuel Efficiency</strong></td>
                                        <td class="px-4 py-2">Identify optimization opportunities</td>
                                    </tr>
                                    <tr class="border-b border-teal border-opacity-50">
                                        <td class="px-4 py-2"><strong>Maintenance Alerts</strong></td>
                                        <td class="px-4 py-2">Never miss a service or license renewal</td>
                                    </tr>
                                    <tr>
                                        <td class="px-4 py-2"><strong>Profitability Insights</strong></td>
                                        <td class="px-4 py-2">Spot your best and worst performing routes</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                    
                    <div class="text-center text-gray-400">
                        Ready to get started? Select an option above or use the navigation menu to explore.
                    </div>
                </div>
            </div>
            
            <!-- Cost & Profitability Tab -->
            <div id="cost-tab" class="p-6 hidden">
                <div class="flex items-center mb-6">
                    <h1 class="text-teal text-3xl font-bold mr-2">Prime Tower</h1>
                    <span class="text-gold text-lg mt-1">Clarity. Control. Growth.</span>
                </div>
                
                <h2 class="text-2xl font-bold mb-4">💵 Cost & Profitability Overview</h2>
                <p class="mb-6">Analyze cost structures and profitability by truck and route</p>
                
                <!-- KPI Cards -->
                <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                    <div class="metric-card bg-navy p-4 rounded-lg border border-teal">
                        <div class="flex items-center">
                            <i class="fas fa-dollar-sign text-teal mr-2"></i>
                            <h3 class="text-sm text-gray-300">Total Revenue</h3>
                        </div>
                        <p class="text-2xl font-bold text-gold mt-1">R245,678.90</p>
                        <div class="text-xs text-green-500 mt-1">↑ 12.5% vs last period</div>
                    </div>
                    <div class="metric-card bg-navy p-4 rounded-lg border border-teal">
                        <div class="flex items-center">
                            <i class="fas fa-money-bill-wave text-teal mr-2"></i>
                            <h3 class="text-sm text-gray-300">Total Cost</h3>
                        </div>
                        <p class="text-2xl font-bold text-gold mt-1">R189,345.20</p>
                        <div class="text-xs text-red-500 mt-1">↓ 8.3% vs last period</div>
                    </div>
                    <div class="metric-card bg-navy p-4 rounded-lg border border-teal">
                        <div class="flex items-center">
                            <i class="fas fa-calculator text-teal mr-2"></i>
                            <h3 class="text-sm text-gray-300">Avg Cost per KM</h3>
                        </div>
                        <p class="text-2xl font-bold text-gold mt-1">R12.45</p>
                    </div>
                    <div class="metric-card bg-navy p-4 rounded-lg border border-teal">
                        <div class="flex items-center">
                            <i class="fas fa-chart-line text-teal mr-2"></i>
                            <h3 class="text-sm text-gray-300">Profitable Trucks</h3>
                        </div>
                        <p class="text-2xl font-bold text-gold mt-1">8 / 10</p>
                    </div>
                </div>
                
                <p class="text-sm text-gray-400 mb-6">Data from March 1, 2023 to March 31, 2023</p>
                
                <!-- Charts -->
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
                    <div class="chart-container">
                        <h3 class="text-lg font-bold mb-4 text-teal">Cost Structure by Truck</h3>
                        <div class="h-80 bg-navy rounded flex items-center justify-center">
                            <p class="text-gray-400">Chart would display here</p>
                        </div>
                    </div>
                    <div class="chart-container">
                        <h3 class="text-lg font-bold mb-4 text-teal">Profit by Truck</h3>
                        <div class="h-80 bg-navy rounded flex items-center justify-center">
                            <p class="text-gray-400">Chart would display here</p>
                        </div>
                    </div>
                </div>
                
                <div class="chart-container mb-6">
                    <h3 class="text-lg font-bold mb-4 text-teal">Route Profitability Analysis</h3>
                    <div class="h-96 bg-navy rounded flex items-center justify-center">
                        <p class="text-gray-400">Bubble chart would display here</p>
                    </div>
                </div>
                
                <div class="bg-red-900 bg-opacity-20 p-4 rounded-lg border border-red-700 mb-6">
                    <div class="flex items-center">
                        <i class="fas fa-exclamation-triangle text-red-500 mr-2"></i>
                        <h3 class="font-bold">🚨 12 trips resulted in losses totaling R45,678.90</h3>
                    </div>
                </div>
                
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <div class="chart-container">
                        <h3 class="text-lg font-bold mb-4 text-teal">Cumulative Loss by Truck</h3>
                        <div class="h-80 bg-navy rounded flex items-center justify-center">
                            <p class="text-gray-400">Chart would display here</p>
                        </div>
                    </div>
                    <div class="chart-container">
                        <h3 class="text-lg font-bold mb-4 text-teal">Cumulative Loss by Route</h3>
                        <div class="h-80 bg-navy rounded flex items-center justify-center">
                            <p class="text-gray-400">Chart would display here</p>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Daily Operations Tab -->
            <div id="operations-tab" class="p-6 hidden">
                <div class="flex items-center mb-6">
                    <h1 class="text-teal text-3xl font-bold mr-2">Prime Tower</h1>
                    <span class="text-gold text-lg mt-1">Clarity. Control. Growth.</span>
                </div>
                
                <h2 class="text-2xl font-bold mb-4">🚛 Daily Operations Tracker</h2>
                <p class="mb-6">Monitor daily truck activities and performance metrics</p>
                
                <!-- KPI Cards -->
                <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                    <div class="metric-card bg-navy p-4 rounded-lg border border-teal">
                        <div class="flex items-center">
                            <i class="fas fa-truck text-teal mr-2"></i>
                            <h3 class="text-sm text-gray-300">Active Trucks</h3>
                        </div>
                        <p class="text-2xl font-bold text-gold mt-1">10</p>
                        <div class="text-xs text-green-500 mt-1">↑ 25.0% vs last period</div>
                    </div>
                    <div class="metric-card bg-navy p-4 rounded-lg border border-teal">
                        <div class="flex items-center">
                            <i class="fas fa-boxes text-teal mr-2"></i>
                            <h3 class="text-sm text-gray-300">Total Tons Moved</h3>
                        </div>
                        <p class="text-2xl font-bold text-gold mt-1">1,245.6</p>
                        <div class="text-xs text-green-500 mt-1">↑ 18.7% vs last period</div>
                    </div>
                    <div class="metric-card bg-navy p-4 rounded-lg border border-teal">
                        <div class="flex items-center">
                            <i class="fas fa-road text-teal mr-2"></i>
                            <h3 class="text-sm text-gray-300">Distance Covered</h3>
                        </div>
                        <p class="text-2xl font-bold text-gold mt-1">15,234 km</p>
                    </div>
                    <div class="metric-card bg-navy p-4 rounded-lg border border-teal">
                        <div class="flex items-center">
                            <i class="fas fa-sign text-teal mr-2"></i>
                            <h3 class="text-sm text-gray-300">Routes Used</h3>
                        </div>
                        <p class="text-2xl font-bold text-gold mt-1">8</p>
                    </div>
                </div>
                
                <p class="text-sm text-gray-400 mb-6">Data from March 1, 2023 to March 31, 2023</p>
                
                <!-- Charts -->
                <div class="chart-container mb-6">
                    <h3 class="text-lg font-bold mb-4 text-teal">Daily Tons Moved</h3>
                    <div class="h-80 bg-navy rounded flex items-center justify-center">
                        <p class="text-gray-400">Line chart would display here</p>
                    </div>
                </div>
                
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
                    <div class="chart-container">
                        <h3 class="text-lg font-bold mb-4 text-teal">Total Tons by Truck</h3>
                        <div class="h-80 bg-navy rounded flex items-center justify-center">
                            <p class="text-gray-400">Chart would display here</p>
                        </div>
                    </div>
                    <div class="chart-container">
                        <h3 class="text-lg font-bold mb-4 text-teal">Total Trips by Truck</h3>
                        <div class="h-80 bg-navy rounded flex items-center justify-center">
                            <p class="text-gray-400">Chart would display here</p>
                        </div>
                    </div>
                </div>
                
                <div class="bg-yellow-900 bg-opacity-20 p-4 rounded-lg border border-yellow-700">
                    <div class="flex items-center">
                        <i class="fas fa-exclamation-triangle text-yellow-500 mr-2"></i>
                        <h3 class="font-bold">🚨 2 trucks had no activity in the selected period.</h3>
                    </div>
                    <div class="overflow-x-auto mt-2">
                        <table class="min-w-full border-collapse">
                            <thead>
                                <tr class="border-b border-teal">
                                    <th class="px-4 py-2 text-left">Truck ID</th>
                                    <th class="px-4 py-2 text-left">Driver Name</th>
                                    <th class="px-4 py-2 text-left">Current Mileage</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr class="border-b border-teal border-opacity-50">
                                    <td class="px-4 py-2">TRK-007</td>
                                    <td class="px-4 py-2">John Smith</td>
                                    <td class="px-4 py-2">245,678 km</td>
                                </tr>
                                <tr>
                                    <td class="px-4 py-2">TRK-012</td>
                                    <td class="px-4 py-2">Sarah Johnson</td>
                                    <td class="px-4 py-2">198,345 km</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
            
            <!-- Fuel Efficiency Tab -->
            <div id="fuel-tab" class="p-6 hidden">
                <div class="flex items-center mb-6">
                    <h1 class="text-teal text-3xl font-bold mr-2">Prime Tower</h1>
                    <span class="text-gold text-lg mt-1">Clarity. Control. Growth.</span>
                </div>
                
                <h2 class="text-2xl font-bold mb-4">⛽ Fuel Efficiency Analysis</h2>
                <p class="mb-6">Monitor fuel consumption patterns and identify optimization opportunities</p>
                
                <!-- KPI Cards -->
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                    <div class="metric-card bg-navy p-4 rounded-lg border border-teal">
                        <div class="flex items-center">
                            <i class="fas fa-tachometer-alt text-teal mr-2"></i>
                            <h3 class="text-sm text-gray-300">Avg Fuel Efficiency</h3>
                        </div>
                        <p class="text-2xl font-bold text-gold mt-1">3.45 km/L</p>
                    </div>
                    <div class="metric-card bg-navy p-4 rounded-lg border border-teal">
                        <div class="flex items-center">
                            <i class="fas fa-gas-pump text-teal mr-2"></i>
                            <h3 class="text-sm text-gray-300">Total Fuel Used</h3>
                        </div>
                        <p class="text-2xl font-bold text-gold mt-1">4,521.1 L</p>
                    </div>
                    <div class="metric-card bg-navy p-4 rounded-lg border border-teal">
                        <div class="flex items-center">
                            <i class="fas fa-dollar-sign text-teal mr-2"></i>
                            <h3 class="text-sm text-gray-300">Avg Fuel Cost per km</h3>
                        </div>
                        <p class="text-2xl font-bold text-gold mt-1">R3.12</p>
                    </div>
                </div>
                
                <p class="text-sm text-gray-400 mb-6">Data from March 1, 2023 to March 31, 2023</p>
                
                <!-- Charts -->
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
                    <div class="chart-container">
                        <h3 class="text-lg font-bold mb-4 text-teal">Daily Fuel Efficiency</h3>
                        <div class="h-80 bg-navy rounded flex items-center justify-center">
                            <p class="text-gray-400">Chart would display here</p>
                        </div>
                    </div>
                    <div class="chart-container">
                        <h3 class="text-lg font-bold mb-4 text-teal">Fuel Efficiency by Truck</h3>
                        <div class="h-80 bg-navy rounded flex items-center justify-center">
                            <p class="text-gray-400">Chart would display here</p>
                        </div>
                    </div>
                </div>
                
                <div class="chart-container mb-6">
                    <h3 class="text-lg font-bold mb-4 text-teal">Fuel Consumption vs Distance</h3>
                    <div class="h-96 bg-navy rounded flex items-center justify-center">
                        <p class="text-gray-400">Scatter plot would display here</p>
                    </div>
                </div>
                
                <div class="bg-red-900 bg-opacity-20 p-4 rounded-lg border border-red-700">
                    <div class="flex items-center">
                        <i class="fas fa-exclamation-triangle text-red-500 mr-2"></i>
                        <h3 class="font-bold">Found 5 trips with efficiency below 2.0 km/L</h3>
                    </div>
                    <div class="overflow-x-auto mt-2">
                        <table class="min-w-full border-collapse">
                            <thead>
                                <tr class="border-b border-teal">
                                    <th class="px-4 py-2 text-left">Date</th>
                                    <th class="px-4 py-2 text-left">Truck ID</th>
                                    <th class="px-4 py-2 text-left">Driver</th>
                                    <th class="px-4 py-2 text-left">Route</th>
                                    <th class="px-4 py-2 text-left">Distance</th>
                                    <th class="px-4 py-2 text-left">Fuel Used</th>
                                    <th class="px-4 py-2 text-left">Efficiency</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr class="border-b border-teal border-opacity-50">
                                    <td class="px-4 py-2">03/15/2023</td>
                                    <td class="px-4 py-2">TRK-005</td>
                                    <td class="px-4 py-2">Mike Brown</td>
                                    <td class="px-4 py-2">RT-AB12</td>
                                    <td class="px-4 py-2">345 km</td>
                                    <td class="px-4 py-2">187 L</td>
                                    <td class="px-4 py-2 text-red-500">1.84 km/L</td>
                                </tr>
                                <!-- More rows would be here -->
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
            
            <!-- Maintenance Tab -->
            <div id="maintenance-tab" class="p-6 hidden">
                <div class="flex items-center mb-6">
                    <h1 class="text-teal text-3xl font-bold mr-2">Prime Tower</h1>
                    <span class="text-gold text-lg mt-1">Clarity. Control. Growth.</span>
                </div>
                
                <h2 class="text-2xl font-bold mb-4">🔧 Maintenance & Compliance</h2>
                <p class="mb-6">Track vehicle maintenance schedules and compliance status</p>
                
                <!-- KPI Cards -->
                <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                    <div class="metric-card bg-navy p-4 rounded-lg border border-teal">
                        <div class="flex items-center">
                            <i class="fas fa-tools text-teal mr-2"></i>
                            <h3 class="text-sm text-gray-300">Overdue Services</h3>
                        </div>
                        <p class="text-2xl font-bold text-gold mt-1">3</p>
                    </div>
                    <div class="metric-card bg-navy p-4 rounded-lg border border-teal">
                        <div class="flex items-center">
                            <i class="fas fa-car text-teal mr-2"></i>
                            <h3 class="text-sm text-gray-300">Vehicle Licenses Expiring</h3>
                        </div>
                        <p class="text-2xl font-bold text-gold mt-1">2</p>
                    </div>
                    <div class="metric-card bg-navy p-4 rounded-lg border border-teal">
                        <div class="flex items-center">
                            <i class="fas fa-id-card text-teal mr-2"></i>
                            <h3 class="text-sm text-gray-300">Driver Licenses Expiring</h3>
                        </div>
                        <p class="text-2xl font-bold text-gold mt-1">1</p>
                    </div>
                    <div class="metric-card bg-navy p-4 rounded-lg border border-teal">
                        <div class="flex items-center">
                            <i class="fas fa-shield-alt text-teal mr-2"></i>
                            <h3 class="text-sm text-gray-300">GIT Insurance Expiring</h3>
                        </div>
                        <p class="text-2xl font-bold text-gold mt-1">0</p>
                    </div>
                </div>
                
                <!-- Charts -->
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
                    <div class="chart-container">
                        <h3 class="text-lg font-bold mb-4 text-teal">KM Since Last Service</h3>
                        <div class="h-80 bg-navy rounded flex items-center justify-center">
                            <p class="text-gray-400">Chart would display here</p>
                        </div>
                    </div>
                    <div class="chart-container">
                        <h3 class="text-lg font-bold mb-4 text-teal">Expiring Licenses & Insurance (Next 30 Days)</h3>
                        <div class="h-80 bg-navy rounded flex items-center justify-center">
                            <p class="text-gray-400">Heatmap would display here</p>
                        </div>
                    </div>
                </div>
                
                <div class="bg-red-900 bg-opacity-20 p-4 rounded-lg border border-red-700 mb-6">
                    <div class="flex items-center">
                        <i class="fas fa-exclamation-triangle text-red-500 mr-2"></i>
                        <h3 class="font-bold">🚨 3 trucks are overdue for service</h3>
                    </div>
                    <div class="overflow-x-auto mt-2">
                        <table class="min-w-full border-collapse">
                            <thead>
                                <tr class="border-b border-teal">
                                    <th class="px-4 py-2 text-left">Truck ID</th>
                                    <th class="px-4 py-2 text-left">Driver Name</th>
                                    <th class="px-4 py-2 text-left">Current Mileage</th>
                                    <th class="px-4 py-2 text-left">Last Service Mileage</th>
                                    <th class="px-4 py-2 text-left">KM Since Service</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr class="border-b border-teal border-opacity-50">
                                    <td class="px-4 py-2">TRK-003</td>
                                    <td class="px-4 py-2">David Wilson</td>
                                    <td class="px-4 py-2">278,456 km</td>
                                    <td class="px-4 py-2">168,900 km</td>
                                    <td class="px-4 py-2 text-red-500">109,556 km</td>
                                </tr>
                                <!-- More rows would be here -->
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <div class="bg-green-900 bg-opacity-20 p-4 rounded-lg border border-green-700">
                    <div class="flex items-center">
                        <i class="fas fa-check-circle text-green-500 mr-2"></i>
                        <h3 class="font-bold">✅ All other trucks are within service limits</h3>
                    </div>
                </div>
            </div>
            
            <!-- Insights Tab -->
            <div id="insights-tab" class="p-6 hidden">
                <div class="flex items-center mb-6">
                    <h1 class="text-teal text-3xl font-bold mr-2">Prime Tower</h1>
                    <span class="text-gold text-lg mt-1">Clarity. Control. Growth.</span>
                </div>
                
                <h2 class="text-2xl font-bold mb-4 text-center border-b border-teal pb-2 inline-block">💡 Strategic Insights</h2>
                <p class="mb-8 text-center">Actionable recommendations to optimize fleet performance</p>
                
                <!-- Performance Dashboard -->
                <div class="mb-12">
                    <h3 class="text-xl font-bold mb-6 text-center">🏆 Performance Dashboard</h3>
                    
                    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
                        <!-- Most Profitable Truck -->
                        <div class="bg-navy p-6 rounded-lg border-l-4 border-teal shadow-lg">
                            <div class="flex items-center gap-4 mb-4">
                                <div class="bg-gold w-12 h-12 rounded-full flex items-center justify-center">
                                    <span class="text-xl">🚛</span>
                                </div>
                                <h4 class="text-gold font-bold text-lg">Most Profitable Truck</h4>
                            </div>
                            <p class="text-sm text-gray-300 mb-1">Truck ID</p>
                            <p class="text-xl font-bold mb-4">TRK-009</p>
                            <p class="text-sm text-gray-300 mb-1">Driver</p>
                            <p class="text-lg mb-6">Robert Johnson</p>
                            <p class="text-sm text-gray-300 mb-1">Total Profit</p>
                            <p class="text-3xl text-teal font-bold">R56,789.20</p>
                        </div>
                        
                        <!-- Most Profitable Route -->
                        <div class="bg-navy p-6 rounded-lg border-l-4 border-teal shadow-lg">
                            <div class="flex items-center gap-4 mb-4">
                                <div class="bg-gold w-12 h-12 rounded-full flex items-center justify-center">
                                    <span class="text-xl">🛣️</span>
                                </div>
                                <h4 class="text-gold font-bold text-lg">Most Profitable Route</h4>
                            </div>
                            <p class="text-sm text-gray-300 mb-1">Route Code</p>
                            <p class="text-xl font-bold mb-6">RT-CD34</p>
                            <p class="text-sm text-gray-300 mb-1">Average Profit</p>
                            <p class="text-3xl text-teal font-bold">R4,567.80</p>
                        </div>
                    </div>
                </div>
                
                <!-- Optimization Opportunities -->
                <div class="mb-12">
                    <h3 class="text-xl font-bold mb-6">⚡ Optimization Opportunities</h3>
                    
                    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        <!-- Least Fuel-Efficient Trucks -->
                        <div class="bg-navy p-6 rounded-lg border-l-4 border-red-500 shadow-lg">
                            <div class="flex items-center gap-4 mb-4">
                                <div class="bg-red-500 w-12 h-12 rounded-full flex items-center justify-center">
                                    <span class="text-xl">⛽</span>
                                </div>
                                <h4 class="text-red-500 font-bold text-lg">Least Fuel-Efficient Trucks</h4>
                            </div>
                            <div class="overflow-x-auto">
                                <table class="min-w-full">
                                    <thead>
                                        <tr class="border-b border-gray-600">
                                            <th class="text-left py-2 text-gray-300">Truck</th>
                                            <th class="text-left py-2 text-gray-300">Driver</th>
                                            <th class="text-right py-2 text-gray-300">Efficiency</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr class="border-b border-gray-700">
                                            <td class="py-2 font-bold">TRK-005</td>
                                            <td class="py-2">Mike Brown</td>
                                            <td class="py-2 text-right text-red-400">2.12 km/L</td>
                                        </tr>
                                        <tr class="border-b border-gray-700">
                                            <td class="py-2 font-bold">TRK-002</td>
                                            <td class="py-2">Lisa Wong</td>
                                            <td class="py-2 text-right text-red-400">2.45 km/L</td>
                                        </tr>
                                        <tr>
                                            <td class="py-2 font-bold">TRK-008</td>
                                            <td class="py-2">Tom Harris</td>
                                            <td class="py-2 text-right text-red-400">2.67 km/L</td>
                                        </tr>
                                    </tbody>
                                </table>
                            </div>
                        </div>
                        
                        <!-- Top Loss-Making Routes -->
                        <div class="bg-navy p-6 rounded-lg border-l-4 border-red-500 shadow-lg">
                            <div class="flex items-center gap-4 mb-4">
                                <div class="bg-red-500 w-12 h-12 rounded-full flex items-center justify-center">
                                    <span class="text-xl">🔴</span>
                                </div>
                                <h4 class="text-red-500 font-bold text-lg">Top Loss-Making Routes</h4>
                            </div>
                            <div class="overflow-x-auto">
                                <table class="min-w-full">
                                    <thead>
                                        <tr class="border-b border-gray-600">
                                            <th class="text-left py-2 text-gray-300">Route Code</th>
                                            <th class="text-right py-2 text-gray-300">Total Loss</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr class="border-b border-gray-700">
                                            <td class="py-2 font-bold">RT-EF56</td>
                                            <td class="py-2 text-right text-red-400">R12,345.60</td>
                                        </tr>
                                        <tr class="border-b border-gray-700">
                                            <td class="py-2 font-bold">RT-GH78</td>
                                            <td class="py-2 text-right text-red-400">R8,765.40</td>
                                        </tr>
                                        <tr>
                                            <td class="py-2 font-bold">RT-IJ90</td>
                                            <td class="py-2 text-right text-red-400">R5,678.90</td>
                                        </tr>
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Pricing Recommendations -->
                <div class="bg-yellow-900 bg-opacity-20 p-6 rounded-lg border border-yellow-700">
                    <h3 class="text-xl font-bold mb-4 flex items-center">
                        <i class="fas fa-money-bill-wave text-yellow-500 mr-2"></i>
                        💰 Pricing Recommendations
                    </h3>
                    <p class="mb-4">The following high-volume routes are currently unprofitable. Consider rate adjustments:</p>
                    <ul class="list-disc pl-5 space-y-2">
                        <li>
                            <strong>RT-AB12</strong>: Current rate R245.60/ton → Suggest R282.44/ton (15% increase)
                        </li>
                        <li>
                            <strong>RT-CD34</strong>: Current rate R287.90/ton → Suggest R331.09/ton (15% increase)
                        </li>
                    </ul>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Simulate login functionality
        function login() {
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            const errorElement = document.getElementById('login-error');
            
            // Simple validation (in a real app, this would be server-side)
            if (username && password) {
                // Hide login screen
                document.getElementById('login-screen').classList.add('hidden');
                // Show dashboard
                document.getElementById('dashboard').classList.remove('hidden');
                // Set username display
                document.getElementById('username-display').textContent = username;
                // Reset form
                document.getElementById('username').value = '';
                document.getElementById('password').value = '';
                errorElement.classList.add('hidden');
            } else {
                errorElement.classList.remove('hidden');
            }
        }
        
        function logout() {
            // Show login screen
            document.getElementById('login-screen').classList.remove('hidden');
            // Hide dashboard
            document.getElementById('dashboard').classList.add('hidden');
        }
        
        // Tab switching functionality
        function switchTab(tabName) {
            // Hide all tabs
            document.querySelectorAll('[id$="-tab"]').forEach(tab => {
                tab.classList.add('hidden');
            });
            
            // Show selected tab
            document.getElementById(`${tabName}-tab`).classList.remove('hidden');
            
            // Update active menu item
            document.querySelectorAll('.menu-item').forEach(item => {
                item.classList.remove('active');
            });
            
            // Find the menu item that matches our tab and make it active
            const menuItems = document.querySelectorAll('.menu-item');
            for (let i = 0; i < menuItems.length; i++) {
                if (menuItems[i].getAttribute('onclick').includes(tabName)) {
                    menuItems[i].classList.add('active');
                    break;
                }
            }
        }
        
        // Demo functions
        function useDemoData() {
            alert('Demo mode enabled! Switch to other tabs to explore.');
        }
        
        function connectSheet() {
            alert('Coming soon! Currently using our demo data.');
        }
        
        function viewTemplate() {
            alert('Template link coming soon');
        }
        
        // Initialize the dashboard with Home tab active
        document.addEventListener('DOMContentLoaded', function() {
            // This would be handled by the login in a real app
            // For demo purposes, we'll simulate a login
            // login();
        });
    </script>
</body>
</html>
