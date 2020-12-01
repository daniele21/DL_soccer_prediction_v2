# tensorboard --logdir logs
import numpy as np
from torch.utils.tensorboard import SummaryWriter, summary

writer = SummaryWriter('./logs', flush_secs=5)

def tb_update_loss(train_loss, eval_loss, index):

    # writer.add_scalar('Loss', train_loss, index)
    writer.add_scalars('Loss', {'Train':train_loss,
                                'Validation':eval_loss}, index)
    writer.flush()
    # writer.close()

def tb_histogram(true, pred, thr=None):

    true_list = np.array(true)
    pred_list = np.array(pred)

    writer.add_histogram('Evaluation', true_list)
    writer.add_histogram('Evaluation', pred_list)

    writer.close()
