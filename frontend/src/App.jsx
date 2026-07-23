import { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Link, useNavigate, useParams, useLocation } from 'react-router-dom';
import axios from 'axios';
import { GraduationCap, Users, LayoutDashboard, ChevronLeft, Search } from 'lucide-react';
import './index.css';

const api = axios.create({
  baseURL: '/api'
});

function Navigation() {
  const location = useLocation();
  return (
    <nav className="header">
      <div className="flex items-center gap-4">
        <GraduationCap size={36} color="var(--accent-color)" />
        <h1 className="header-title">EIS Platform</h1>
      </div>
      <div className="nav-links">
        <Link to="/" className={`nav-link flex items-center gap-2 ${location.pathname === '/' ? 'active' : ''}`}>
          <Users size={18} /> Students
        </Link>
        <Link to="/summary" className={`nav-link flex items-center gap-2 ${location.pathname === '/summary' ? 'active' : ''}`}>
          <LayoutDashboard size={18} /> Summary
        </Link>
      </div>
    </nav>
  );
}

function StudentList() {
  const [students, setStudents] = useState([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchStudents = async () => {
      setLoading(true);
      try {
        const res = await api.get(`/students/?search=${search}`);
        setStudents(res.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    
    const timeoutId = setTimeout(() => {
      fetchStudents();
    }, 300); // debounce search
    
    return () => clearTimeout(timeoutId);
  }, [search]);

  return (
    <div className="panel">
      <div className="flex items-center gap-2 mb-4">
        <Search size={20} color="var(--text-secondary)" style={{ position: 'absolute', marginLeft: '16px' }} />
        <input 
          type="text" 
          className="input-search" 
          style={{ paddingLeft: '48px', marginBottom: 0 }}
          placeholder="Search students by name..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {loading ? <div className="loader"></div> : (
        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Admission No</th>
                <th>Name</th>
                <th>Class</th>
                <th>Section</th>
                <th>DOB</th>
                <th>Average</th>
              </tr>
            </thead>
            <tbody>
              {students.map(student => (
                <tr key={student.admission_no} onClick={() => navigate(`/student/${student.admission_no}`)}>
                  <td>{student.admission_no}</td>
                  <td style={{ fontWeight: 500 }}>{student.name}</td>
                  <td>{student.class}</td>
                  <td>{student.section}</td>
                  <td>{student.dob}</td>
                  <td>
                    {student.average !== null ? (
                      <span className="badge badge-present">{student.average}%</span>
                    ) : (
                      <span className="badge badge-absent">N/A</span>
                    )}
                  </td>
                </tr>
              ))}
              {students.length === 0 && (
                <tr>
                  <td colSpan="6" className="text-center" style={{ padding: '40px' }}>
                    No students found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function StudentDetail() {
  const { id } = useParams();
  const [student, setStudent] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchStudent = async () => {
      try {
        const res = await api.get(`/students/${id}/`);
        setStudent(res.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchStudent();
  }, [id]);

  if (loading) return <div className="panel"><div className="loader"></div></div>;
  if (!student) return <div className="panel"><p>Student not found.</p></div>;

  return (
    <div className="panel">
      <button className="btn btn-secondary flex items-center gap-2 mb-4" onClick={() => navigate(-1)}>
        <ChevronLeft size={16} /> Back
      </button>
      
      <div className="flex justify-between items-center mb-4">
        <div>
          <h2 style={{ fontSize: '32px', marginBottom: '8px' }}>{student.name}</h2>
          <p style={{ color: 'var(--text-secondary)' }}>
            Admission No: {student.admission_no} &nbsp;|&nbsp; 
            Class: {student.class} {student.section} &nbsp;|&nbsp; 
            DOB: {student.dob}
          </p>
        </div>
        <div style={{ textAlign: 'right' }}>
          <div className="card-title">Total / Average</div>
          <div className="card-value">
            {student.total} <span style={{ fontSize: '20px', color: 'var(--text-secondary)', fontWeight: 400 }}>/ {student.average ?? 'N/A'}%</span>
          </div>
        </div>
      </div>

      <div className="grid mt-4">
        {student.marks.map((mark, idx) => (
          <div className="card" key={idx}>
            <div className="card-title">{mark.subject}</div>
            <div className="card-value mt-4">
              {mark.marks_obtained !== null ? (
                <span>{mark.marks_obtained}</span>
              ) : (
                <span className="badge badge-absent" style={{ fontSize: '14px', padding: '6px 12px' }}>Absent</span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function Summary() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await api.get('/summary/');
        setData(res.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) return <div className="panel"><div className="loader"></div></div>;
  if (!data) return null;

  return (
    <div>
      <h2 style={{ marginBottom: '24px', fontSize: '24px' }}>Class Performance</h2>
      
      <div className="grid mb-4">
        {Object.entries(data.subject_stats).map(([subject, stats]) => (
          <div className="tooltip-container" key={subject}>
            <div className="card">
              <div className="card-title">{subject} Average</div>
              <div className="card-value" style={{ color: 'var(--accent-color)' }}>{stats.average}%</div>
            </div>
            <div className="tooltip-content">
              <div className="tooltip-header">Top 5 in {subject}</div>
              {stats.top_students.map((student, idx) => (
                <div className="tooltip-row" key={idx}>
                  <span className="tooltip-name">{student.name}</span>
                  <span className="tooltip-score">{student.marks}</span>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      {data.top_student && (
        <div className="tooltip-container">
          <div className="panel mt-4 flex justify-between items-center" style={{ background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.2), rgba(16, 185, 129, 0.1))' }}>
            <div>
              <div className="card-title" style={{ color: 'var(--text-primary)' }}>Top Student by Total Marks</div>
              <div className="card-value">{data.top_student.name}</div>
              <div style={{ color: 'var(--text-secondary)', marginTop: '8px' }}>Admission No: {data.top_student.admission_no}</div>
            </div>
            <div style={{ textAlign: 'right' }}>
              <div className="card-title">Total Marks</div>
              <div className="card-value" style={{ fontSize: '48px', color: 'var(--success-color)' }}>
                {data.top_student.total_marks}
              </div>
            </div>
          </div>
          <div className="tooltip-content" style={{ width: '300px' }}>
            <div className="tooltip-header">Top 5 by Total Marks</div>
            {data.top_5_students.map((student, idx) => (
              <div className="tooltip-row" key={idx}>
                <span className="tooltip-name">{student.name}</span>
                <span className="tooltip-score" style={{ color: 'var(--success-color)' }}>{student.total_marks}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <div className="container">
        <Navigation />
        <Routes>
          <Route path="/" element={<StudentList />} />
          <Route path="/student/:id" element={<StudentDetail />} />
          <Route path="/summary" element={<Summary />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
