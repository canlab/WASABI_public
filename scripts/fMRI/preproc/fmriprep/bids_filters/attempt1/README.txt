The point of these bids filters were hopefully to prep a series of bold-epi images with missing anterior headcoils by registering it with its closest-in-time T1w image with a missing anterior headcoil + a lesion mask. Turns out:

1. fmriprep can only tolerate one lesion mask per participant at a time. The bids filter will not filter out lesion masks from other sessions, even with the roi flag in the filter .json file. This should be brought up to the BIDS community.
2. Discovery has strange sharding issues in the /dartfs-hpc/scratch/$USER space, which can result in invalid "out of space" errors that will crash fmriprep. This has been brought up to Dartmouth-RC and they are looking into it...
3. fmriprep and PyBIDS does not really tolerate invalid flags in the json file such as "_comment": . So those have to be taken out in the bids-filter.json files.
4. fmriprep and PyBIDS does not really tolerate the "subject" flag in the bids-filter.json file. Instead use the -s flag (for subject) in the singularity fmriprep command.

Perhaps the best way to go going forward is to have a BIDS directory only with a single lesion mask for each participant with headcoil issues. Then run fmriprep once with a filter only of subjects with lesions, and then run fmriprep with a filter only of subjects without lesions. 
