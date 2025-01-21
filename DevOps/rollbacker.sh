#!/bin/sh

# Check if commit hash and branch name are provided as arguments
if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Error, both commit hash ID and branch name are required as arguments"
    echo "Usage: ./rollback_to_previous.sh <commit-hash> <branch-name>"
    exit 1
fi

# Store the commit hash and branch name passed as arguments
COMMIT_HASH=$1
BRANCH_NAME=$2


# Check if the commit exists in the repository
git cat-file commit "$COMMIT_HASH" >/dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Error, The commit hash '$COMMIT_HASH' does not exist"
    exit 1
fi

# Check if the specified branch exists
git show-ref --verify --quiet "refs/heads/$BRANCH_NAME"
if [ $? -ne 0 ]; then
    echo "Error, branch '$BRANCH_NAME' does not exist"
    exit 1
fi

# Switch to the specified branch
echo "Switching to branch '$BRANCH_NAME'..."
git checkout "$BRANCH_NAME"
if [ $? -ne 0 ]; then
    echo "Error, failed to switch to branch '$BRANCH_NAME'"
    exit 1
fi



# Revert the given commit safely
echo "Reverting commit $COMMIT_HASH..."

# Perform the revert (this creates a new commit that undoes the changes of the specified commit)
git revert --no-commit "$COMMIT_HASH"

# Check if revert was successful
if [ $? -ne 0 ]; then
    echo "Error: failed to revert"
    exit 1
fi


echo "Commit reverted successfully, committing the changes..."

# Commit the revert
git commit -m "Reverted commit $COMMIT_HASH to return to previous state"

# Push the changes to the remote repository (use appropriate branch name)
echo "Pushing the changes to the remote repository..."
git push origin "$BRANCH_NAME"

# Final success message
echo "Rollback to previous state complete and changes pushed to remote repo"
