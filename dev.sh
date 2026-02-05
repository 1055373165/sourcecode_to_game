#!/bin/bash
#
# Study with Challenge Game - 服务管理脚本
# 用法: ./dev.sh [start|stop|restart|status]
#

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
BACKEND_PID_FILE="$PROJECT_ROOT/.backend.pid"
FRONTEND_PID_FILE="$PROJECT_ROOT/.frontend.pid"
BACKEND_LOG="$PROJECT_ROOT/backend.log"
FRONTEND_LOG="$PROJECT_ROOT/frontend.log"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[$(date '+%H:%M:%S')]${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}!${NC} $1"
}

# 启动后端
start_backend() {
    print_status "正在启动后端服务..."
    
    if [ -f "$BACKEND_PID_FILE" ]; then
        local pid=$(cat "$BACKEND_PID_FILE")
        if ps -p $pid > /dev/null 2>&1; then
            print_warning "后端服务已在运行 (PID: $pid)"
            return 0
        fi
    fi
    
    cd "$BACKEND_DIR"
    nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > "$BACKEND_LOG" 2>&1 &
    echo $! > "$BACKEND_PID_FILE"
    
    # 等待服务启动
    sleep 2
    if curl -s --connect-timeout 3 http://127.0.0.1:8000/health > /dev/null 2>&1; then
        print_success "后端服务启动成功 (http://localhost:8000)"
        print_status "Swagger 文档: http://localhost:8000/docs"
    else
        print_error "后端服务启动失败，请查看日志: $BACKEND_LOG"
        return 1
    fi
}

# 启动前端
start_frontend() {
    print_status "正在启动前端服务..."
    
    if [ -f "$FRONTEND_PID_FILE" ]; then
        local pid=$(cat "$FRONTEND_PID_FILE")
        if ps -p $pid > /dev/null 2>&1; then
            print_warning "前端服务已在运行 (PID: $pid)"
            return 0
        fi
    fi
    
    cd "$FRONTEND_DIR"
    nohup npm run dev > "$FRONTEND_LOG" 2>&1 &
    echo $! > "$FRONTEND_PID_FILE"
    
    # 等待服务启动
    sleep 3
    if curl -s --connect-timeout 3 http://127.0.0.1:5173 > /dev/null 2>&1; then
        print_success "前端服务启动成功 (http://localhost:5173)"
    else
        print_error "前端服务启动失败，请查看日志: $FRONTEND_LOG"
        return 1
    fi
}

# 停止后端
stop_backend() {
    print_status "正在停止后端服务..."
    
    if [ -f "$BACKEND_PID_FILE" ]; then
        local pid=$(cat "$BACKEND_PID_FILE")
        if ps -p $pid > /dev/null 2>&1; then
            kill $pid 2>/dev/null
            sleep 1
            # 强制终止如果还在运行
            if ps -p $pid > /dev/null 2>&1; then
                kill -9 $pid 2>/dev/null
            fi
        fi
        rm -f "$BACKEND_PID_FILE"
    fi
    
    # 额外清理可能的uvicorn进程
    pkill -f "uvicorn app.main:app" 2>/dev/null
    
    print_success "后端服务已停止"
}

# 停止前端
stop_frontend() {
    print_status "正在停止前端服务..."
    
    if [ -f "$FRONTEND_PID_FILE" ]; then
        local pid=$(cat "$FRONTEND_PID_FILE")
        if ps -p $pid > /dev/null 2>&1; then
            kill $pid 2>/dev/null
            sleep 1
            if ps -p $pid > /dev/null 2>&1; then
                kill -9 $pid 2>/dev/null
            fi
        fi
        rm -f "$FRONTEND_PID_FILE"
    fi
    
    # 额外清理可能的vite进程
    pkill -f "vite" 2>/dev/null
    
    print_success "前端服务已停止"
}

# 检查服务状态
check_status() {
    echo ""
    echo "═══════════════════════════════════════════"
    echo "       Study with Challenge 服务状态"
    echo "═══════════════════════════════════════════"
    echo ""
    
    # 检查后端
    if curl -s --connect-timeout 2 http://127.0.0.1:8000/health > /dev/null 2>&1; then
        print_success "后端服务: 运行中 (http://localhost:8000)"
    else
        print_error "后端服务: 未运行"
    fi
    
    # 检查前端
    if curl -s --connect-timeout 2 http://127.0.0.1:5173 > /dev/null 2>&1; then
        print_success "前端服务: 运行中 (http://localhost:5173)"
    else
        print_error "前端服务: 未运行"
    fi
    
    echo ""
}

# 显示帮助
show_help() {
    echo ""
    echo "Study with Challenge 开发服务管理脚本"
    echo ""
    echo "用法: $0 [命令]"
    echo ""
    echo "命令:"
    echo "  start     启动所有服务"
    echo "  stop      停止所有服务"
    echo "  restart   重启所有服务"
    echo "  status    查看服务状态"
    echo "  logs      查看服务日志"
    echo "  help      显示此帮助信息"
    echo ""
}

# 查看日志
show_logs() {
    echo ""
    echo "═══════════════ 后端日志 ═══════════════"
    if [ -f "$BACKEND_LOG" ]; then
        tail -20 "$BACKEND_LOG"
    else
        echo "无日志文件"
    fi
    
    echo ""
    echo "═══════════════ 前端日志 ═══════════════"
    if [ -f "$FRONTEND_LOG" ]; then
        tail -20 "$FRONTEND_LOG"
    else
        echo "无日志文件"
    fi
    echo ""
}

# 主命令处理
case "$1" in
    start)
        echo ""
        echo "═══════════════════════════════════════════"
        echo "    启动 Study with Challenge 开发服务"
        echo "═══════════════════════════════════════════"
        echo ""
        start_backend
        start_frontend
        echo ""
        check_status
        ;;
    stop)
        echo ""
        echo "═══════════════════════════════════════════"
        echo "    停止 Study with Challenge 开发服务"
        echo "═══════════════════════════════════════════"
        echo ""
        stop_frontend
        stop_backend
        echo ""
        ;;
    restart)
        echo ""
        echo "═══════════════════════════════════════════"
        echo "    重启 Study with Challenge 开发服务"
        echo "═══════════════════════════════════════════"
        echo ""
        stop_frontend
        stop_backend
        sleep 2
        start_backend
        start_frontend
        echo ""
        check_status
        ;;
    status)
        check_status
        ;;
    logs)
        show_logs
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        if [ -z "$1" ]; then
            show_help
        else
            print_error "未知命令: $1"
            show_help
        fi
        ;;
esac
