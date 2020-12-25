from scripts.data.postprocessing import postprocessing_test_data
from scripts.models.evaluation import thr_analysis, evaluate_results
from scripts.models.model_inference import model_inference
from scripts.models.strategy import simulation
from scripts.visualization.summary import show_summary


def data_inference(test_data, model, feat_eng, params):

    # Required Params : [league_name, league_dir,
    #                    n_prev_match, field,
    #                    test_size, save_dir]

    field = params['field']

    testset = test_data[field]
    testset = testset[testset['f-opponent'].isnull() == False]

    pred, true = model_inference(testset, feat_eng, model,
                                 model_name=params['field'],
                                 train=params['train'])

    return pred, true

def simulate(test_data, pred, true, params):

    # Required Params : [field, save_dir,
    #                    thr, thr_list,
    #                    n_matches, money_bet,
    #                    combo_list, plot]

    field = params['field']
    thr = params['thr']
    plot = params['plot'] if 'plot' in list(params.keys()) else True

    testset = test_data[field]
    testset = testset[testset['f-opponent'].isnull() == False]

    pred_df, _, _ = evaluate_results(true, pred, params,
                                     plot=plot)

    data_result = postprocessing_test_data(testset, pred_df)

    _, thr_outcomes, _ = thr_analysis(true, pred, params)
    thr_outcome = thr_outcomes[str(thr)]

    summary, sim_result, _ = simulation(data_result, params,
                                        thr_outcome,
                                        plot=plot)

    show_summary(summary)

