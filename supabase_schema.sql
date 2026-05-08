-- Create elections table
CREATE TABLE elections (
    year INTEGER PRIMARY KEY,
    total_constituencies INTEGER,
    total_electorate BIGINT,
    total_votes_polled BIGINT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create constituencies table
CREATE TABLE constituencies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    election_year INTEGER REFERENCES elections(year) ON DELETE CASCADE,
    constituency_number VARCHAR(10),
    constituency_name VARCHAR(255) NOT NULL,
    seats INTEGER DEFAULT 1,
    electorate BIGINT,
    votes_polled BIGINT,
    nota_votes BIGINT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(election_year, constituency_name)
);

-- Create candidates table
CREATE TABLE candidates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    constituency_id UUID REFERENCES constituencies(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    sex VARCHAR(10),
    party VARCHAR(100),
    votes BIGINT NOT NULL,
    vote_percentage DECIMAL(5, 2),
    rank INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for faster querying
CREATE INDEX idx_constituencies_year ON constituencies(election_year);
CREATE INDEX idx_candidates_constituency ON candidates(constituency_id);
CREATE INDEX idx_candidates_party ON candidates(party);
CREATE INDEX idx_candidates_rank ON candidates(rank);
