from cls_market.aggregator_data import get_aggregator
from cls_market.dso_data import get_dso

agg = get_aggregator("AGG_001", cost_model="normalized")
dso = get_dso("DSO_001", cost_model="normalized")

print("Aggregator:", agg.aggregator_id)
print("Kosten bei Nennleistung:", agg.true_cost(agg.p_nom_kw))
print("Kosten bei Mindestleistung:", agg.true_cost(agg.p_min_kw))

print("DSO:", dso.dso_id)
print("Netzreferenz K:", dso.network_limit_kw)
print("Kosten bei K:", dso.cost(dso.network_limit_kw))

agg_normalized = get_aggregator("AGG_001", "normalized")
agg_heinrich = get_aggregator("AGG_001", "heinrich_exponential")

print("Aggregator:", agg_normalized.aggregator_id)
print("Kosten bei Nennleistung:", agg_normalized.true_cost(agg.p_nom_kw))
print("Kosten bei Mindestleistung:", agg_normalized.true_cost(agg.p_min_kw))

print("Aggregator:", agg_heinrich.aggregator_id)
print("Kosten bei Nennleistung:", agg_heinrich.true_cost(agg.p_nom_kw))
print("Kosten bei Mindestleistung:", agg_heinrich.true_cost(agg.p_min_kw))

print(agg_heinrich.true_cost(500))
print(agg_normalized.true_cost(500))