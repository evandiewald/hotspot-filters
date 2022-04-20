


detailed_receipt_sql = """
select

rx_address as address,
count(distinct tx_address) 		as n_witnessed,
count(tx_address) 		        as total_witnessed,
percentile_cont(0.5) WITHIN GROUP (ORDER BY distance_km)				as med_distance,
max(distance_km)				as max_distance,
avg(tx_reward_scale) 			as avg_tx_reward_scale,
stddev(tx_reward_scale) 		as std_tx_reward_scale,
sum(tx_on_denylist) 			as n_denylisted_tx,
regr_r2(witness_signal, distance_km) as r2_rssi_distance,
regr_slope(witness_signal, distance_km) as slope_rssi_distance,
regr_r2(witness_signal, witness_snr) as r2_rssi_snr,
regr_slope(witness_signal, witness_snr) as slope_rssi_snr,

(CASE WHEN
	stddev(witness_signal) = 0 THEN 0
	ELSE
		3*(avg(witness_signal) - percentile_cont(0.5) WITHIN GROUP (ORDER BY witness_signal)) / stddev(witness_signal)
END)		 					as skew_rssi,

(CASE WHEN
	stddev(witness_snr) = 0 THEN 0
	ELSE
		3*(avg(witness_snr) - percentile_cont(0.5) WITHIN GROUP (ORDER BY witness_snr)) / stddev(witness_snr)
END)		 					as skew_snr,

sum(
	CASE WHEN
	tx_payer = rx_payer THEN 1
	ELSE 0
	END
)::float / count(tx_address) as same_maker_ratio,

(select value from follower_info where name = 'sync_height') - avg(tx_first_block) as avg_tx_age_blocks,
stddev(tx_first_block) as std_tx_first_block,

max(rx_on_denylist)             as rx_on_denylist

from detailed_receipts
group by rx_address;

"""


data_transfer_sql = """
select 
client, 
sum(num_dcs) as dcs_transferred, 
sum(num_packets) as packets_transferred
from data_credits
group by client;
"""


n_blocks_sql = """
select (select value from follower_info where name = 'sync_height') - (select value from follower_info where name = 'first_block');
"""


