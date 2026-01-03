#!/bin/bash
#
# detect-stack.sh - Detect technology stack from a codebase
#
# Usage:
#     bash detect-stack.sh <path-to-project>
#
# Output:
#     JSON with detected technologies
#
# This script provides fast, deterministic detection of:
# - Project type (nodejs, python, go, rust, java, ruby, flutter)
# - Package manager (npm, yarn, pnpm, pip, poetry, cargo, etc.)
# - Web frameworks (express, fastapi, django, flask, gin, etc.)
# - ORM/Database (prisma, typeorm, sqlalchemy, mongoose, etc.)
# - Architecture pattern (layered, feature-based, mvc, clean)
# - CI/CD (github-actions, gitlab-ci, jenkins, etc.)

set -e

PROJECT_DIR="${1:-.}"

if [[ ! -d "$PROJECT_DIR" ]]; then
    echo '{"error": "Directory not found: '"$PROJECT_DIR"'"}'
    exit 1
fi

cd "$PROJECT_DIR"

# Initialize detection arrays
PROJECT_TYPE=""
PACKAGE_MANAGER=""
FRAMEWORKS=""
ORMS=""
ARCHITECTURE=""
CI_CD=""

# ============================================================================
# Project Type Detection
# ============================================================================

detect_project_type() {
    if [[ -f "package.json" ]]; then
        PROJECT_TYPE="nodejs"
        if [[ -f "yarn.lock" ]]; then
            PACKAGE_MANAGER="yarn"
        elif [[ -f "pnpm-lock.yaml" ]]; then
            PACKAGE_MANAGER="pnpm"
        elif [[ -f "bun.lockb" ]]; then
            PACKAGE_MANAGER="bun"
        else
            PACKAGE_MANAGER="npm"
        fi
    elif [[ -f "pyproject.toml" ]]; then
        PROJECT_TYPE="python"
        if grep -q "poetry" pyproject.toml 2>/dev/null; then
            PACKAGE_MANAGER="poetry"
        elif grep -q "pdm" pyproject.toml 2>/dev/null; then
            PACKAGE_MANAGER="pdm"
        else
            PACKAGE_MANAGER="pip"
        fi
    elif [[ -f "requirements.txt" ]] || [[ -f "setup.py" ]]; then
        PROJECT_TYPE="python"
        PACKAGE_MANAGER="pip"
    elif [[ -f "go.mod" ]]; then
        PROJECT_TYPE="go"
        PACKAGE_MANAGER="go-modules"
    elif [[ -f "Cargo.toml" ]]; then
        PROJECT_TYPE="rust"
        PACKAGE_MANAGER="cargo"
    elif [[ -f "pom.xml" ]]; then
        PROJECT_TYPE="java"
        PACKAGE_MANAGER="maven"
    elif [[ -f "build.gradle" ]] || [[ -f "build.gradle.kts" ]]; then
        PROJECT_TYPE="java"
        PACKAGE_MANAGER="gradle"
    elif [[ -f "Gemfile" ]]; then
        PROJECT_TYPE="ruby"
        PACKAGE_MANAGER="bundler"
    elif [[ -f "pubspec.yaml" ]]; then
        PROJECT_TYPE="flutter"
        PACKAGE_MANAGER="pub"
    elif [[ -f "mix.exs" ]]; then
        PROJECT_TYPE="elixir"
        PACKAGE_MANAGER="mix"
    else
        PROJECT_TYPE="unknown"
        PACKAGE_MANAGER="unknown"
    fi
}

# ============================================================================
# Framework Detection
# ============================================================================

detect_frameworks() {
    local frameworks=()

    # Node.js frameworks
    if [[ -f "package.json" ]]; then
        local pkg_content
        pkg_content=$(cat package.json 2>/dev/null || echo "{}")

        # Express
        if echo "$pkg_content" | grep -q '"express"'; then
            frameworks+=("express")
        fi
        # Fastify
        if echo "$pkg_content" | grep -q '"fastify"'; then
            frameworks+=("fastify")
        fi
        # NestJS
        if echo "$pkg_content" | grep -q '"@nestjs/core"'; then
            frameworks+=("nestjs")
        fi
        # Next.js
        if echo "$pkg_content" | grep -q '"next"'; then
            frameworks+=("nextjs")
        fi
        # Hono
        if echo "$pkg_content" | grep -q '"hono"'; then
            frameworks+=("hono")
        fi
        # Koa
        if echo "$pkg_content" | grep -q '"koa"'; then
            frameworks+=("koa")
        fi
    fi

    # Python frameworks
    if [[ "$PROJECT_TYPE" == "python" ]]; then
        local py_deps=""
        [[ -f "requirements.txt" ]] && py_deps+=$(cat requirements.txt 2>/dev/null)
        [[ -f "pyproject.toml" ]] && py_deps+=$(cat pyproject.toml 2>/dev/null)

        if echo "$py_deps" | grep -qi "fastapi"; then
            frameworks+=("fastapi")
        fi
        if echo "$py_deps" | grep -qi "django"; then
            frameworks+=("django")
        fi
        if echo "$py_deps" | grep -qi "flask"; then
            frameworks+=("flask")
        fi
        if echo "$py_deps" | grep -qi "starlette"; then
            frameworks+=("starlette")
        fi
    fi

    # Go frameworks
    if [[ -f "go.mod" ]]; then
        local go_mod
        go_mod=$(cat go.mod 2>/dev/null || echo "")

        if echo "$go_mod" | grep -q "gin-gonic/gin"; then
            frameworks+=("gin")
        fi
        if echo "$go_mod" | grep -q "labstack/echo"; then
            frameworks+=("echo")
        fi
        if echo "$go_mod" | grep -q "gofiber/fiber"; then
            frameworks+=("fiber")
        fi
    fi

    # Ruby frameworks
    if [[ -f "Gemfile" ]]; then
        if grep -q "rails" Gemfile 2>/dev/null; then
            frameworks+=("rails")
        fi
        if grep -q "sinatra" Gemfile 2>/dev/null; then
            frameworks+=("sinatra")
        fi
    fi

    # Java frameworks
    if [[ -f "pom.xml" ]] || [[ -f "build.gradle" ]] || [[ -f "build.gradle.kts" ]]; then
        local java_deps=""
        [[ -f "pom.xml" ]] && java_deps+=$(cat pom.xml 2>/dev/null)
        [[ -f "build.gradle" ]] && java_deps+=$(cat build.gradle 2>/dev/null)
        [[ -f "build.gradle.kts" ]] && java_deps+=$(cat build.gradle.kts 2>/dev/null)

        if echo "$java_deps" | grep -qi "spring-boot"; then
            frameworks+=("spring-boot")
        fi
    fi

    # Convert to JSON array
    if [[ ${#frameworks[@]} -eq 0 ]]; then
        FRAMEWORKS="[]"
    else
        FRAMEWORKS=$(printf '%s\n' "${frameworks[@]}" | jq -R . | jq -s .)
    fi
}

# ============================================================================
# ORM Detection
# ============================================================================

detect_orms() {
    local orms=()

    # Node.js ORMs
    if [[ -f "package.json" ]]; then
        local pkg_content
        pkg_content=$(cat package.json 2>/dev/null || echo "{}")

        if echo "$pkg_content" | grep -q '"@prisma/client"' || [[ -f "prisma/schema.prisma" ]] || [[ -f "schema.prisma" ]]; then
            orms+=("prisma")
        fi
        if echo "$pkg_content" | grep -q '"typeorm"'; then
            orms+=("typeorm")
        fi
        if echo "$pkg_content" | grep -q '"sequelize"'; then
            orms+=("sequelize")
        fi
        if echo "$pkg_content" | grep -q '"mongoose"'; then
            orms+=("mongoose")
        fi
        if echo "$pkg_content" | grep -q '"drizzle-orm"'; then
            orms+=("drizzle")
        fi
        if echo "$pkg_content" | grep -q '"kysely"'; then
            orms+=("kysely")
        fi
    fi

    # Python ORMs
    if [[ "$PROJECT_TYPE" == "python" ]]; then
        local py_deps=""
        [[ -f "requirements.txt" ]] && py_deps+=$(cat requirements.txt 2>/dev/null)
        [[ -f "pyproject.toml" ]] && py_deps+=$(cat pyproject.toml 2>/dev/null)

        if echo "$py_deps" | grep -qi "sqlalchemy"; then
            orms+=("sqlalchemy")
        fi
        if echo "$py_deps" | grep -qi "django"; then
            orms+=("django-orm")
        fi
        if echo "$py_deps" | grep -qi "tortoise-orm"; then
            orms+=("tortoise")
        fi
        if echo "$py_deps" | grep -qi "peewee"; then
            orms+=("peewee")
        fi
    fi

    # Go ORMs
    if [[ -f "go.mod" ]]; then
        local go_mod
        go_mod=$(cat go.mod 2>/dev/null || echo "")

        if echo "$go_mod" | grep -q "gorm.io/gorm"; then
            orms+=("gorm")
        fi
        if echo "$go_mod" | grep -q "ent/ent"; then
            orms+=("ent")
        fi
    fi

    # Ruby ORMs
    if [[ -f "Gemfile" ]]; then
        if grep -q "activerecord" Gemfile 2>/dev/null || grep -q "rails" Gemfile 2>/dev/null; then
            orms+=("activerecord")
        fi
    fi

    # Convert to JSON array
    if [[ ${#orms[@]} -eq 0 ]]; then
        ORMS="[]"
    else
        ORMS=$(printf '%s\n' "${orms[@]}" | jq -R . | jq -s .)
    fi
}

# ============================================================================
# Architecture Pattern Detection
# ============================================================================

detect_architecture() {
    local patterns=()

    # Check for common directory patterns
    if [[ -d "src/domain" ]] || [[ -d "src/application" ]] || [[ -d "src/infrastructure" ]]; then
        patterns+=("clean-architecture")
    fi

    if [[ -d "src/models" ]] && [[ -d "src/controllers" ]] && [[ -d "src/views" ]]; then
        patterns+=("mvc")
    elif [[ -d "app/models" ]] && [[ -d "app/controllers" ]] && [[ -d "app/views" ]]; then
        patterns+=("mvc")
    fi

    if [[ -d "src/services" ]] && [[ -d "src/repositories" ]]; then
        patterns+=("layered")
    elif [[ -d "src/models" ]] && [[ -d "src/services" ]] && [[ -d "src/controllers" ]]; then
        patterns+=("layered")
    fi

    # Feature-based detection (look for feature folders)
    local feature_dirs=0
    for dir in src/features src/modules src/auth src/users src/tasks src/api; do
        [[ -d "$dir" ]] && ((feature_dirs++))
    done
    if [[ $feature_dirs -ge 2 ]]; then
        patterns+=("feature-based")
    fi

    # Serverless
    if [[ -f "serverless.yml" ]] || [[ -f "serverless.yaml" ]] || [[ -d "functions" ]] || [[ -d "lambda" ]]; then
        patterns+=("serverless")
    fi

    # Microservices
    if [[ -f "docker-compose.yml" ]] || [[ -f "docker-compose.yaml" ]]; then
        # Check if it defines multiple services
        local service_count
        service_count=$(grep -c "^\s*[a-zA-Z_-]*:$" docker-compose.yml 2>/dev/null || echo "0")
        if [[ $service_count -gt 2 ]]; then
            patterns+=("microservices")
        fi
    fi

    # Monorepo
    if [[ -f "lerna.json" ]] || [[ -f "pnpm-workspace.yaml" ]] || [[ -d "packages" ]]; then
        patterns+=("monorepo")
    fi

    # Convert to JSON array
    if [[ ${#patterns[@]} -eq 0 ]]; then
        ARCHITECTURE="[]"
    else
        ARCHITECTURE=$(printf '%s\n' "${patterns[@]}" | jq -R . | jq -s .)
    fi
}

# ============================================================================
# CI/CD Detection
# ============================================================================

detect_cicd() {
    local cicd=()

    if [[ -d ".github/workflows" ]]; then
        cicd+=("github-actions")
    fi
    if [[ -f ".gitlab-ci.yml" ]]; then
        cicd+=("gitlab-ci")
    fi
    if [[ -f "Jenkinsfile" ]]; then
        cicd+=("jenkins")
    fi
    if [[ -f ".circleci/config.yml" ]]; then
        cicd+=("circleci")
    fi
    if [[ -f ".travis.yml" ]]; then
        cicd+=("travis")
    fi
    if [[ -f "azure-pipelines.yml" ]]; then
        cicd+=("azure-devops")
    fi
    if [[ -f "bitbucket-pipelines.yml" ]]; then
        cicd+=("bitbucket")
    fi

    # Convert to JSON array
    if [[ ${#cicd[@]} -eq 0 ]]; then
        CI_CD="[]"
    else
        CI_CD=$(printf '%s\n' "${cicd[@]}" | jq -R . | jq -s .)
    fi
}

# ============================================================================
# File Presence Detection
# ============================================================================

detect_files() {
    local files_json="{"
    local first=true

    # Key files to check
    local files_to_check=(
        "package.json"
        "tsconfig.json"
        "pyproject.toml"
        "requirements.txt"
        "go.mod"
        "Cargo.toml"
        "Gemfile"
        "Dockerfile"
        "docker-compose.yml"
        ".env.example"
        "README.md"
        "CLAUDE.md"
    )

    for file in "${files_to_check[@]}"; do
        if [[ "$first" == "true" ]]; then
            first=false
        else
            files_json+=","
        fi

        if [[ -f "$file" ]]; then
            files_json+="\"$file\":true"
        else
            files_json+="\"$file\":false"
        fi
    done

    # Check directories
    local dirs_to_check=(
        ".github/workflows"
        "src"
        "tests"
        "prisma"
    )

    for dir in "${dirs_to_check[@]}"; do
        files_json+=","
        if [[ -d "$dir" ]]; then
            files_json+="\"$dir\":true"
        else
            files_json+="\"$dir\":false"
        fi
    done

    files_json+="}"
    echo "$files_json"
}

# ============================================================================
# Main
# ============================================================================

detect_project_type
detect_frameworks
detect_orms
detect_architecture
detect_cicd
FILES_FOUND=$(detect_files)

# Output JSON
cat <<EOF
{
  "project_type": "$PROJECT_TYPE",
  "package_manager": "$PACKAGE_MANAGER",
  "frameworks": $FRAMEWORKS,
  "orms": $ORMS,
  "architecture": $ARCHITECTURE,
  "ci_cd": $CI_CD,
  "files_found": $FILES_FOUND,
  "scanned_path": "$(pwd)"
}
EOF
