document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.post-card').forEach(card => {
        const likeBtn = card.querySelector('.btn-like');
        const commentToggleBtn = card.querySelector('.btn-comment-toggle');
        const addCartBtn = card.querySelector('.btn-add-cart');
        const commentForm = card.querySelector('.comment-form');
        const commentInput = card.querySelector('.comment-input');
        const submitCommentBtn = card.querySelector('.btn-submit-comment');
        const countLike = card.querySelector('.count-like');
        const countComment = card.querySelector('.count-comment');
        const countCart = card.querySelector('.count-cart');

        if (likeBtn && countLike) {
            likeBtn.addEventListener('click', () => {
                const current = parseInt(countLike.textContent, 10) || 0;
                if (countLike.textContent === "0") {
                    countLike.textContent = current + 1;
                }
                else {
                    countLike.textContent = current - 1;
                }
            });
        }

        if (addCartBtn && countCart) {
            addCartBtn.addEventListener('click', () => {
                const current = parseInt(countCart.textContent, 10) || 0;
                countCart.textContent = current + 1;
                alert("!Añadido al carrito!")
            });
        }

        if (commentToggleBtn && commentForm) {
            commentToggleBtn.addEventListener('click', () => {
                commentForm.classList.toggle('hidden');
            });
        }

        if (submitCommentBtn && countComment && commentInput && commentForm) {
            submitCommentBtn.addEventListener('click', () => {
                const current = parseInt(countComment.textContent, 10) || 0;
                countComment.textContent = current + 1;
                commentInput.value = '';
                commentForm.classList.add('hidden');
            });
        }
    });
});