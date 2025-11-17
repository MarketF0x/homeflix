from server.core.db import get_session
from server.core.models import Video

with get_session() as s:
    videos = s.query(Video).all()
    durations = [v.duration_seconds//60 for v in videos if v.duration_seconds]
    
    print(f'Total videos: {len(videos)}')
    print(f'Avec durée: {len(durations)}')
    if durations:
        print(f'Min: {min(durations)} min')
        print(f'Max: {max(durations)} min')
        print(f'<= 65 min (séries): {len([d for d in durations if d <= 65])}')
        print(f'>= 70 min (films): {len([d for d in durations if d >= 70])}')
        print(f'Entre 65-70 min (zone grise): {len([d for d in durations if 65 < d < 70])}')
        
        # Exemples de vidéos dans chaque catégorie
        series = [v for v in videos if v.duration_seconds and v.duration_seconds//60 <= 65]
        films = [v for v in videos if v.duration_seconds and v.duration_seconds//60 >= 70]
        
        print(f'\nExemples de séries (3 premiers):')
        for v in series[:3]:
            print(f'  - {v.title}: {v.duration_seconds//60} min')
        
        print(f'\nExemples de films (3 premiers):')
        for v in films[:3]:
            print(f'  - {v.title}: {v.duration_seconds//60} min')
