import re
from pydriller import Repository
from pydriller.domain.commit import ModificationType

def analyze_tika_issues():
    repo_url = "https://github.com/apache/tika"
    issue_ids = ["TIKA-6", "TIKA-172", "TIKA-605", "TIKA-1722", "TIKA-3523"]
    
    patterns = [re.compile(rf"\b{issue_id}\b", re.IGNORECASE) for issue_id in issue_ids]
    
    target_changes = {ModificationType.ADD, ModificationType.MODIFY, ModificationType.DELETE}
    
    found_commits = []
    total_valid_files = 0
    dmm_scores = []

    print(f"Analyzing repository: {repo_url}...")

    for commit in Repository(repo_url).traverse_commits():
        if any(pattern.search(commit.msg) for pattern in patterns):
            found_commits.append(commit.hash)
            
            count_for_this_commit = 0
            for file in commit.modified_files:
                if file.change_type in target_changes:
                    count_for_this_commit += 1
            
            total_valid_files += count_for_this_commit
            
            metrics = [
                commit.dmm_unit_size,
                commit.dmm_unit_complexity,
                commit.dmm_unit_interfacing
            ]
            valid_metrics = [m for m in metrics if m is not None]
            
            if valid_metrics:
                dmm_scores.append(sum(valid_metrics) / len(valid_metrics))
            else:
                dmm_scores.append(0)

    total_commits = len(found_commits)
    avg_files = total_valid_files / total_commits if total_commits > 0 else 0
    avg_dmm = sum(dmm_scores) / total_commits if total_commits > 0 else 0

    print("-" * 30)
    print(f"total commits analyzed: {total_commits}")
    print(f"average number of files changed: {avg_files:.2f}")
    print(f"average DMM metrics: {avg_dmm:.4f}")
    print("-" * 30)

if __name__ == "__main__":
    analyze_tika_issues()