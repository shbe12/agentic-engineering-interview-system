-- AI Mock Interview Agent — schema

create table if not exists candidates (
    id uuid primary key default gen_random_uuid(),
    name text,
    resume_text text not null,
    resume_sections jsonb not null default '{}'::jsonb,
    field text not null default 'other', -- 'nlp' | 'cv' | 'other'
    created_at timestamptz not null default now()
);

create table if not exists interview_sessions (
    id uuid primary key default gen_random_uuid(),
    candidate_id uuid not null references candidates(id) on delete cascade,
    current_phase int not null default 1,
    status text not null default 'in_progress', -- 'in_progress' | 'completed'
    started_at timestamptz not null default now(),
    completed_at timestamptz
);

create table if not exists interview_messages (
    id uuid primary key default gen_random_uuid(),
    session_id uuid not null references interview_sessions(id) on delete cascade,
    phase int not null,
    role text not null, -- 'interviewer' | 'candidate'
    content text not null,
    audio_meta jsonb,
    created_at timestamptz not null default now()
);

create table if not exists phase_evaluations (
    id uuid primary key default gen_random_uuid(),
    session_id uuid not null references interview_sessions(id) on delete cascade,
    phase int not null,
    score numeric,
    notes text,
    created_at timestamptz not null default now(),
    unique (session_id, phase)
);

create table if not exists final_reports (
    id uuid primary key default gen_random_uuid(),
    session_id uuid not null references interview_sessions(id) on delete cascade unique,
    summary text not null,
    per_phase_scores jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now()
);

create index if not exists idx_interview_messages_session on interview_messages(session_id);
create index if not exists idx_phase_evaluations_session on phase_evaluations(session_id);
