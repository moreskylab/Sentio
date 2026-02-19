from django.shortcuts import render
from rest_framework import viewsets
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Article
from .serializers import ArticleSerializer
from .vector_db import VectorService


# --- NEW: CRUD API ---
class ArticleViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Articles to be viewed or edited.
    Standard CRUD:
    - GET /api/articles/ (List all)
    - POST /api/articles/ (Create)
    - GET /api/articles/{id}/ (Retrieve one)
    - PUT/PATCH /api/articles/{id}/ (Update)
    - DELETE /api/articles/{id}/ (Delete)

    *NOTE*: No Vector logic is needed here.
    The 'signals.py' file handles the sync to LanceDB automatically.
    """
    queryset = Article.objects.all().order_by('-created_at')
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticated]  # Blocks non-logged in users


# --- EXISTING: Recommendation Logic ---
@login_required
@csrf_exempt
def recommend_articles(request):
    # ... (Keep your existing recommendation code exactly as is) ...
    # Just ensuring you don't delete your search logic!
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            service = VectorService()
            query_vector = None

            if 'query' in data:
                query_vector = service.get_embedding(data['query'])
            elif 'article_id' in data:
                try:
                    article = Article.objects.get(id=data['article_id'])
                    text = f"{article.title}. {article.content}"
                    query_vector = service.get_embedding(text)
                except Article.DoesNotExist:
                    return JsonResponse({'error': 'Article not found'}, status=404)

            if not query_vector:
                return JsonResponse({'error': 'Invalid input'}, status=400)

            results = service.search_similar(query_vector, top_k=5)

            response_data = []
            for res in results:
                response_data.append({
                    'id': res['id'],
                    'title': res['title'],
                    'similarity_score': 1 - res['_distance']
                })

            return JsonResponse({'recommendations': response_data})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'POST method required'}, status=405)

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')