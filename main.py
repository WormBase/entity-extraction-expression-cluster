import argparse
import datetime
import logging
import os
import re

from wbtools.literature.corpus import CorpusManager

logger = logging.getLogger(__name__)

SEARCH_SENTENCES = ['Gene Expression Omnibus', 'ArrayExpress', 'differentially expressed', 'differential expression']


def main():
    parser = argparse.ArgumentParser(description="String matching pipeline for antibody")
    parser.add_argument("-N", "--db-name", metavar="db_name", dest="db_name", type=str)
    parser.add_argument("-U", "--db-user", metavar="db_user", dest="db_user", type=str)
    parser.add_argument("-P", "--db-password", metavar="db_password", dest="db_password", type=str, default="")
    parser.add_argument("-H", "--db-host", metavar="db_host", dest="db_host", type=str)
    parser.add_argument("-y", "--ssh-host", metavar="ssh_host", dest="ssh_host",
                        type=str)
    parser.add_argument("-w", "--ssh-username", metavar="ssh_user", dest="ssh_user",
                        type=str)
    parser.add_argument("-z", "--ssh-password", metavar="ssh_password", dest="ssh_password",
                        type=str)
    parser.add_argument("-l", "--log-file", metavar="log_file", dest="log_file", type=str, default=None,
                        help="path to log file")
    parser.add_argument("-L", "--log-level", dest="log_level", choices=['DEBUG', 'INFO', 'WARNING', 'ERROR',
                                                                        'CRITICAL'], default="INFO",
                        help="set the logging level")
    parser.add_argument("-f", "--from-date", metavar="from_date", dest="from_date", type=str,
                        help="use only articles included in WB on or after the specified date")
    parser.add_argument("-d", "--working-dir", metavar="working_dir", dest="working_dir", type=str)

    args = parser.parse_args()
    logging.basicConfig(filename=args.log_file, level=args.log_level,
                        format='%(asctime)s - %(name)s - %(levelname)s:%(message)s')

    cm = CorpusManager()
    os.makedirs(args.working_dir, exist_ok=True)
    all_files = sorted([f for f in os.listdir(args.working_dir) if os.path.isfile(os.path.join(args.working_dir, f))])
    latest_file = all_files[-1] if all_files else None
    from_date = latest_file.split("_")[0] if latest_file else args.from_date
    exclude_ids = [line.split("\t")[0].replace("WBPaper", "") for line in open(
        os.path.join(args.working_dir, latest_file))] if latest_file else []
    cm.load_from_wb_database(
        args.db_name, args.db_user, args.db_password, args.db_host, from_date=from_date, exclude_ids=exclude_ids,
        pap_types=["Journal_article"])
    logger.info("Finished loading papers from DB")
    match_regex_arr = [re.compile(r"(?i)[\s\(\[\{\.,;:\'\"\<](" + search_sent + ")[\s\.;:,'\"\)\]\}\>\?]") for
                       search_sent in SEARCH_SENTENCES]
    pap_sent_matches = {}
    for paper in cm.get_all_papers():
        logger.info("Extracting Expression Cluster info from paper " + paper.paper_id)
        fulltext = paper.get_text_docs(include_supplemental=True, return_concatenated=True)
        fulltext = fulltext.replace('\n', ' ')
        pap_sent_matches[paper.paper_id] = [(search_sent, len(re.findall(match_regex, fulltext))) for
                                            match_regex, search_sent in zip(match_regex_arr, SEARCH_SENTENCES)]
    file_name = datetime.datetime.now().strftime("%Y%m%d") + "_" + from_date + "_results.csv"
    if sum([num_match for sent_match in pap_sent_matches.values() for _, num_match in sent_match]) > 0:
        logger.info("Found one or more papers matching search criteria")
        with open(os.path.join(args.working_dir, file_name), 'w') as out_file:
            for pap_id, sent_matches in pap_sent_matches.items():
                if sum([num_match for _, num_match in sent_matches]) > 0:
                    out_file.write("WBPaper" + str(pap_id) + "\t" + str(sum([num_match for _, num_match in sent_matches])) +
                                   "\t" + " ".join([sent + "(" + str(num_match) + ")" for sent, num_match in
                                                    sent_matches]) + "\n")
    else:
        logger.info("No papers matched")
    logger.info("Finished")


if __name__ == '__main__':
    main()
