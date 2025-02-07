html_template = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Search4Faces Report</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        :root {
            --bg-color: #ffffff;
            --text-color: #212529;
            --card-bg: #f8f9fa;
        }

        [data-theme="dark"] {
            --bg-color: #1a1a1a;
            --text-color: #e0e0e0;
            --card-bg: #2d2d2d;
        }

        body {
            background-color: var(--bg-color);
            color: var(--text-color);
            transition: all 0.3s;
            min-height: 100vh;
        }

        .header-section {
            text-align: center;
            margin-bottom: 2rem;
        }

        .person-card {
            background: var(--card-bg);
            border-radius: 15px;
            margin: 15px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            height: 100%;
        }

        .profile-photo-link {
            display: block;
            width: 100%;
            height: 300px;
            border-radius: 8px;
            overflow: hidden;
            margin-bottom: 15px;
        }

        .profile-photo {
            width: 100%;
            height: 100%;
            object-fit: contain;
            transition: transform 0.3s;
        }

        .profile-photo:hover {
            transform: scale(1.05);
        }

        .theme-switcher {
            position: fixed;
            bottom: 30px;
            right: 30px;
            width: 50px;
            height: 50px;
            border-radius: 50%;
            background: linear-gradient(45deg, #ff6b6b, #ff8e53);
            border: none;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            transition: all 0.3s;
            cursor: pointer;
        }

        .theme-switcher:hover {
            transform: rotate(180deg) scale(1.1);
        }

        .score-indicator {
            font-size: 1.1em;
            padding: 8px 15px;
            border-radius: 20px;
            color: white;
            display: inline-block;
            cursor: help;
        }

        .score-high {
            background: linear-gradient(45deg, #28a745, #218838);
        }

        .score-low {
            background: linear-gradient(45deg, #dc3545, #c82333);
        }

        .person-name {
            font-size: 1.5rem;
            margin-bottom: 1rem;
        }

        .detail-item {
            margin-bottom: 0.5rem;
        }

        .detail-label {
            font-weight: 600;
            color: #6c757d;
        }

        [data-theme="dark"] .detail-label {
            color: #adb5bd;
        }
    </style>
</head>
<body>
    <div class="container py-5">
        <div class="header-section">
            <h1>Найдено людей: <strong id="total-count">{{ total }}</strong></h1>
        </div>
        <div class="row">
            {% for person in people %}
            <div class="col-lg-6 mb-4">
                <div class="person-card">
                    <a href="{{ person.profile }}" class="profile-photo-link" target="_blank">
                        <img src="{{ person.source }}" 
                             class="profile-photo" 
                             alt="Фото профиля"
                             loading="lazy">
                    </a>
                    
                    <div class="person-info">
                        <a href="{{ person.profile }}" class="person-name text-decoration-none" target="_blank">
                            {{ person.first_name }} {{ person.last_name }}
                        </a>
                        
                        <div class="score-indicator {{ 'score-high' if person.score >= 50 else 'score-low' }}"
                             title="{% if person.score >= 50 %}Высокое совпадение (>50%){% else %}Низкое совпадение (≤50%){% endif %}"
                             data-bs-toggle="tooltip">
                            {{ "%.1f"|format(person.score) }}%
                        </div>

                        <div class="mt-3">
                            <div class="detail-item">
                                <span class="detail-label">Город:</span>
                                {{ person.city or '—' }}
                            </div>
                            <div class="detail-item">
                                <span class="detail-label">Страна:</span>
                                {{ person.country or '—' }}
                            </div>
                            <div class="detail-item">
                                <span class="detail-label">Возраст:</span>
                                {{ person.age or '—' }}
                            </div>
                            <div class="detail-item">
                                <span class="detail-label">Дата рождения:</span>
                                {{ person.born or '—' }}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>

    <button class="theme-switcher" onclick="toggleTheme()">🌓</button>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        function toggleTheme() {
            const isDark = document.body.getAttribute('data-theme') === 'dark';
            document.body.setAttribute('data-theme', isDark ? 'light' : 'dark');
            localStorage.setItem('theme', isDark ? 'light' : 'dark');
        }

        // Инициализация темы
        document.addEventListener('DOMContentLoaded', () => {
            const savedTheme = localStorage.getItem('theme') || 'light';
            document.body.setAttribute('data-theme', savedTheme);
            
            // Инициализация подсказок
            const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
            [...tooltips].forEach(t => new bootstrap.Tooltip(t));
        });
    </script>
</body>
</html>
""" 