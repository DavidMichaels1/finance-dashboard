import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { BarChart, Bar, XAxis, YAxis, Tooltip, Legend, PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';
import './App.css';

// The base URL of our FastAPI backend
const API = 'http://127.0.0.1:8000';

// Colours for the pie chart slices
const COLORS = ['#6366f1', '#06b6d4', '#f59e0b', '#10b981', '#f43f5e', '#8b5cf6', '#64748b'];

function App() {
  // useState stores data that the component needs to display
  // When state changes, React automatically re-renders the component
  const [monthly, setMonthly] = useState([]);
  const [categories, setCategories] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);

  // useEffect runs once when the component first loads
  // We use it to fetch data from our API
  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fire all three API calls at the same time for speed
        const [monthlyRes, categoriesRes, transactionsRes] = await Promise.all([
          axios.get(`${API}/summary/monthly`),
          axios.get(`${API}/summary/categories`),
          axios.get(`${API}/transactions`),
        ]);

        // Format monthly data — make spending positive for charting
        const monthlyData = monthlyRes.data.map(row => ({
          month: row.month,
          spent: Math.abs(row.total_spent),
          income: row.total_income,
        }));

        setMonthly(monthlyData);
        setCategories(categoriesRes.data);
        setTransactions(transactionsRes.data);
      } catch (err) {
        console.error('Failed to fetch data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Aggregate categories across all months for the pie chart
  const pieData = categories.reduce((acc, row) => {
    const existing = acc.find(r => r.category === row.category);
    if (existing) {
      existing.spent += row.spent;
    } else {
      acc.push({ category: row.category, spent: row.spent });
    }
    return acc;
  }, []);

  if (loading) return <div className="loading">Loading dashboard...</div>;

  return (
    <div className="dashboard">
      <header className="header">
        <h1>Finance Dashboard</h1>
        <p>Personal spending overview</p>
      </header>

      {/* Summary cards */}
      <div className="cards">
        {monthly.map(m => (
          <div className="card" key={m.month}>
            <div className="card-month">{m.month}</div>
            <div className="card-spent">R{m.spent.toLocaleString()}</div>
            <div className="card-label">spent</div>
            <div className="card-income">R{m.income.toLocaleString()} income</div>
          </div>
        ))}
      </div>

      {/* Monthly bar chart */}
      <div className="chart-box">
        <h2>Monthly spending vs income</h2>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={monthly} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
            <XAxis dataKey="month" />
            <YAxis />
            <Tooltip formatter={(value) => `R${value.toLocaleString()}`} />
            <Legend />
            <Bar dataKey="spent" fill="#6366f1" name="Spent" radius={[4,4,0,0]} />
            <Bar dataKey="income" fill="#10b981" name="Income" radius={[4,4,0,0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Category pie chart */}
      <div className="chart-box">
        <h2>Spending by category</h2>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={pieData}
              dataKey="spent"
              nameKey="category"
              cx="50%"
              cy="50%"
              outerRadius={110}
              label={({ category, percent }) => `${category} ${(percent * 100).toFixed(0)}%`}
            >
              {pieData.map((_, index) => (
                <Cell key={index} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip formatter={(value) => `R${value.toLocaleString()}`} />
          </PieChart>
        </ResponsiveContainer>
      </div>

      {/* Transactions table */}
      <div className="chart-box">
        <h2>All transactions</h2>
        <table className="table">
          <thead>
            <tr>
              <th>Date</th>
              <th>Description</th>
              <th>Category</th>
              <th>Amount</th>
            </tr>
          </thead>
          <tbody>
            {transactions.map((t, i) => (
              <tr key={i}>
                <td>{t.date.slice(0, 10)}</td>
                <td>{t.description}</td>
                <td><span className={`badge badge-${t.category.replace(' ', '-')}`}>{t.category}</span></td>
                <td className={t.amount < 0 ? 'negative' : 'positive'}>
                  R{Math.abs(t.amount).toLocaleString()}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default App;