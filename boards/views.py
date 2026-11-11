from django.shortcuts import get_object_or_404, render

from .models import Board, Thread


def board_list(request):
    boards = Board.objects.filter(is_active=True)
    return render(request, 'boards/board_list.html', {'boards': boards})


def board_detail(request, slug):
    board = get_object_or_404(Board, slug=slug, is_active=True)
    threads = board.threads.select_related('author').prefetch_related('posts')
    return render(request, 'boards/board_detail.html', {'board': board, 'threads': threads})


def thread_detail(request, board_slug, pk):
    board = get_object_or_404(Board, slug=board_slug, is_active=True)
    thread = get_object_or_404(Thread, pk=pk, board=board)
    posts = thread.posts.select_related('author').prefetch_related('attachments')
    return render(request, 'boards/thread_detail.html', {'board': board, 'thread': thread, 'posts': posts})
