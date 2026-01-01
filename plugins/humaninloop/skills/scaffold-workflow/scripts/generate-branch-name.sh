#!/usr/bin/env bash
#
# generate-branch-name.sh - Generate a clean branch slug from a feature description
#
# Usage: generate-branch-name.sh "<feature_description>"
# Output: branch-slug (e.g., "user-auth-oauth2")
#
# Behavior:
#   - Filters common stop words (I, want, add, the, to, for, with, etc.)
#   - Preserves technical terms and acronyms (OAuth2, API, JWT, SSO)
#   - Uses lowercase with hyphens as separators
#   - Limits output to 3-4 meaningful words
#   - Minimum 3 characters per word (except recognized acronyms)
#
# Examples:
#   ./generate-branch-name.sh "I want to add user authentication"
#   # Output: user-authentication
#
#   ./generate-branch-name.sh "Implement OAuth2 integration for the API"
#   # Output: oauth2-integration-api
#
#   ./generate-branch-name.sh "Create a dashboard for analytics"
#   # Output: dashboard-analytics
#

set -e

# Input validation
FEATURE_DESCRIPTION="$1"
if [ -z "$FEATURE_DESCRIPTION" ]; then
    echo "Usage: $0 <feature_description>" >&2
    echo "Example: $0 'Add user authentication with OAuth2'" >&2
    exit 1
fi

# Function to clean and format a branch name
clean_branch_name() {
    local name="$1"
    echo "$name" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/-\+/-/g' | sed 's/^-//' | sed 's/-$//'
}

# Function to generate branch name with stop word filtering and length filtering
generate_branch_name() {
    local description="$1"

    # Common stop words to filter out
    local stop_words="^(i|a|an|the|to|for|of|in|on|at|by|with|from|is|are|was|were|be|been|being|have|has|had|do|does|did|will|would|should|could|can|may|might|must|shall|this|that|these|those|my|your|our|their|want|need|add|get|set|create|build|make|implement|please)$"

    # Convert to lowercase and split into words
    local clean_name=$(echo "$description" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/ /g')

    # Filter words: remove stop words and words shorter than 3 chars (unless they're uppercase acronyms in original)
    local meaningful_words=()
    for word in $clean_name; do
        # Skip empty words
        [ -z "$word" ] && continue

        # Keep words that are NOT stop words AND (length >= 3 OR are potential acronyms)
        if ! echo "$word" | grep -qiE "$stop_words"; then
            if [ ${#word} -ge 3 ]; then
                meaningful_words+=("$word")
            elif echo "$description" | grep -q "\b${word^^}\b"; then
                # Keep short words if they appear as uppercase in original (likely acronyms)
                meaningful_words+=("$word")
            fi
        fi
    done

    # If we have meaningful words, use first 3-4 of them
    if [ ${#meaningful_words[@]} -gt 0 ]; then
        local max_words=3
        if [ ${#meaningful_words[@]} -eq 4 ]; then max_words=4; fi

        local result=""
        local count=0
        for word in "${meaningful_words[@]}"; do
            if [ $count -ge $max_words ]; then break; fi
            if [ -n "$result" ]; then result="$result-"; fi
            result="$result$word"
            count=$((count + 1))
        done
        echo "$result"
    else
        # Fallback to original logic if no meaningful words found
        local cleaned=$(clean_branch_name "$description")
        echo "$cleaned" | tr '-' '\n' | grep -v '^$' | head -3 | tr '\n' '-' | sed 's/-$//'
    fi
}

# Generate and output the branch name
generate_branch_name "$FEATURE_DESCRIPTION"
