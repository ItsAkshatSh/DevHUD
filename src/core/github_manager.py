from github import Github
from PyQt5.QtCore import QObject, pyqtSignal
import threading
import time

class GitHubManager(QObject):
    activity_updated = pyqtSignal(list) 
    issues_updated = pyqtSignal(list)    
    prs_updated = pyqtSignal(list)
    repos_updated = pyqtSignal(int)  # Changed to emit just the count
    
    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.github = None
        self.user = None
        self.running = False
        self.update_thread = None
        self.update_interval = 300  # 5 minutes
        
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
                self.update_repos()  # Add repository updates
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
        """Update pull requests"""
        if not self.user:
            return
            
        try:
            # Use search issues endpoint to find PRs with proper query format
            query = f"is:pr author:{self.user.login}"
            print(f"Searching PRs with query: {query}")
            prs = self.github.search_issues(query=query)
            
            # Convert to list of PR objects
            pr_list = []
            for pr in prs:
                if pr.pull_request:  # Ensure it's a PR
                    pr_list.append({
                        'number': pr.number,
                        'title': pr.title,
                        'repo': pr.repository.name,
                        'created_at': pr.created_at,
                        'state': pr.state,
                        'updated_at': pr.updated_at
                    })
            
            print(f"Found {len(pr_list)} PRs")
            self.prs_updated.emit(pr_list)
        except Exception as e:
            print(f"Error updating PRs: {e}")

    def update_repos(self):
        """Update repository count"""
        if not self.user:
            return
            
        try:
            repos = self.user.get_repos()
            repo_count = sum(1 for _ in repos)  # Count total repositories
            self.repos_updated.emit(repo_count)
        except Exception as e:
            print(f"Error updating repos: {e}")
            
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

    def authenticate(self):
        """Authenticate with GitHub"""
        token = self.settings.get('github_token')
        username = self.settings.get('github_username')
        
        if not token or not username:
            print("GitHub token or username not set in settings")
            return False
            
        try:
            print(f"Attempting to authenticate with GitHub as {username}")
            self.github = Github(token)
            # Verify token by getting user info
            self.user = self.github.get_user()
            print(f"Successfully authenticated as {self.user.login}")
            return True
        except Exception as e:
            print(f"GitHub authentication error: {e}")
            self.github = None
            self.user = None
            return False  