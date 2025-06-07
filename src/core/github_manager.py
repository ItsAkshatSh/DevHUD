from github import Github
from PyQt5.QtCore import QObject, pyqtSignal
import threading
import time

class GitHubManager(QObject):
    activity_updated = pyqtSignal(list) 
    issues_updated = pyqtSignal(list)    
    prs_updated = pyqtSignal(list)    
    
    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.github = None
        self.user = None
        self.running = False
        self.update_thread = None
        self.update_interval = 300  
        
        self.init_github()
        
    def init_github(self):
        """Initialize GitHub connection"""
        token = self.settings.get('github_token')
        username = self.settings.get('github_username')
        if token and username:
            try:
                self.github = Github(token)
                self.user = self.github.get_user(username)
                return True
            except Exception as e:
                print(f"Failed to initialize GitHub: {e}")
        return False
        
    def start_monitoring(self):
        """Start monitoring GitHub activity"""
        if not self.running and self.github and self.user:
            self.running = True
            self.update_thread = threading.Thread(target=self._monitor_loop)
            self.update_thread.daemon = True
            self.update_thread.start()
            
    def stop_monitoring(self):
        """Stop monitoring GitHub activity"""
        self.running = False
        if self.update_thread:
            self.update_thread.join()
            
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                self.update_activity()
                self.update_issues()
                self.update_prs()
            except Exception as e:
                print(f"Error updating GitHub data: {e}")
            time.sleep(self.update_interval)
            
    def update_activity(self):
        """Update activity feed"""
        if not self.user:
            return
            
        try:
            events = self.user.get_events()
            activity = []
            for event in events[:10]: 
                activity.append({
                    'type': event.type,
                    'repo': event.repo.name if event.repo else 'Unknown',
                    'created_at': event.created_at,
                    'payload': event.payload
                })
            self.activity_updated.emit(activity)
        except Exception as e:
            print(f"Error updating activity: {e}")
            
    def update_issues(self):
        """Update issues list"""
        if not self.user:
            return
            
        try:
            issues = self.user.get_issues(state='open')
            issue_list = []
            for issue in issues:
                issue_list.append({
                    'number': issue.number,
                    'title': issue.title,
                    'repo': issue.repository.name,
                    'created_at': issue.created_at,
                    'labels': [label.name for label in issue.labels],
                    'comments': issue.comments
                })
            self.issues_updated.emit(issue_list)
        except Exception as e:
            print(f"Error updating issues: {e}")
            
    def update_prs(self):
        """Update pull requests list"""
        if not self.user:
            return
            
        try:
            pulls = self.user.get_pulls(state='open')
            pr_list = []
            for pr in pulls:
                pr_list.append({
                    'number': pr.number,
                    'title': pr.title,
                    'repo': pr.repository.name,
                    'created_at': pr.created_at,
                    'base': pr.base.ref,
                    'head': pr.head.ref,
                    'comments': pr.comments,
                    'review_comments': pr.review_comments
                })
            self.prs_updated.emit(pr_list)
        except Exception as e:
            print(f"Error updating PRs: {e}")
            
    def create_issue(self, title, body, labels=None):
        """Create a new issue"""
        if not self.user:
            return None
            
        try:
            return self.user.create_issue(
                title=title,
                body=body,
                labels=labels or []
            )
        except Exception as e:
            print(f"Error creating issue: {e}")
            return None
            
    def create_pull_request(self, title, body, base='main', head=None):
        """Create a new pull request"""
        if not self.user or not head:
            return None
            
        try:
            return self.user.create_pull(
                title=title,
                body=body,
                base=base,
                head=head
            )
        except Exception as e:
            print(f"Error creating PR: {e}")
            return None
            
    def set_token(self, token):
        """Set GitHub access token"""
        self.settings.set('github_token', token)
        return self.init_github()
        
    def set_username(self, username):
        """Set GitHub username"""
        self.settings.set('github_username', username)
        return self.init_github()
        
    def set_update_interval(self, interval):
        """Set update interval in seconds"""
        self.update_interval = max(60, interval)  