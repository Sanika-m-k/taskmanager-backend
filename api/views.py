from rest_framework import viewsets, permissions, status, generics
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import Project, Task
from .serializers import UserSerializer, ProjectSerializer, ProjectDetailSerializer, TaskSerializer
from rest_framework.decorators import action

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserSerializer

class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = (permissions.IsAuthenticated,)
    
    def get_queryset(self):
        return Project.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = ProjectDetailSerializer(instance)
        return Response(serializer.data)

class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = (permissions.IsAuthenticated,)
    
    def get_queryset(self):
        queryset = Task.objects.filter(project__user=self.request.user)
        
        # Filter by project if provided
        project_id = self.request.query_params.get('project', None)
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        # Filter by status if provided
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
            
        return queryset
    
    def perform_create(self, serializer):
        # Check if project belongs to the user
        project_id = self.request.data.get('project')
        if project_id:
            try:
                project = Project.objects.get(id=project_id, user=self.request.user)
                serializer.save(project=project)
            except Project.DoesNotExist:
                return Response(
                    {"error": "Project not found or not owned by user"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                {"error": "Project ID is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )