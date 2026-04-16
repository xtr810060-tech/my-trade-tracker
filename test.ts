import axios from 'axios';

async function test() {
  try {
    const res = await axios.post('http://localhost:3000/api/auth/register', {
      name: 'Tom',
      email: 'test@test.com',
      password: 'password123'
    });
    console.log("Success:", res.data);
  } catch (err: any) {
    console.error("Error:", err.response?.data || err.message);
  }
}

test();
