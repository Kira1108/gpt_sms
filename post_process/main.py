from preprocess import load_raw_data, preprocess_pipeline, TransformPipeline
from normalize import CleanLoanService, CleanNoisyPrimary, CleanNoisySecondary


if __name__ == "__main__":
    df = load_raw_data("data/ng_message_ai.db")
    df = preprocess_pipeline(df)

    normalize_pipeline = TransformPipeline([
        CleanLoanService(),
        CleanNoisyPrimary(),
        CleanNoisySecondary()]
    )

    df = normalize_pipeline(df)
    
    print(df.head())
    
    
    df.copy().reset_index(drop = True).to_feather("data/normalized.feather")