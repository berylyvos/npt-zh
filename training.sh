CUDA_VISIBLE_DEVICES=0 python train.py data-bin/ \
--arch convtransformer --optimizer adam --adam-betas '(0.9, 0.98)' --clip-norm 0.0 \
--lr-scheduler inverse_sqrt --warmup-init-lr 1e-07 --warmup-updates 4000 --lr 0.0001 \
--min-lr 1e-09 --criterion label_smoothed_cross_entropy --label-smoothing 0.1 \
--weight-decay 0.0 --max-tokens 4096  \
--save-dir checkpoints/ \
--no-progress-bar --log-format simple --log-interval 2000 \
--find-unused-parameters --ddp-backend=no_c10d	\
--max-epoch 10
