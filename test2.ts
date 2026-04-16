import axios from 'axios';

async function test() {
  try {
    const regRes = await axios.post('http://localhost:3000/api/auth/register', {
      name: 'Tom',
      email: 'test2@test.com',
      password: 'password123'
    });
    const token = regRes.data.token;
    
    const res = await axios.get('http://localhost:3000/api/trades', {
      headers: { Authorization: `Bearer ${token}` }
    });
    console.log("Trades:", res.data);
    console.log("IsArray:", Array.isArray(res.data));
  } catch (err: any) {
    console.error("Error:", err.response?.data || err.message);
  }
}

test();
