--
-- PostgreSQL database dump
--

-- Dumped from database version 14.17 (Ubuntu 14.17-0ubuntu0.22.04.1)
-- Dumped by pg_dump version 14.17 (Ubuntu 14.17-0ubuntu0.22.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: ztn
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO ztn;

--
-- Name: headquarters_wallet; Type: TABLE; Schema: public; Owner: ztn
--

CREATE TABLE public.headquarters_wallet (
    id integer NOT NULL,
    balance double precision
);


ALTER TABLE public.headquarters_wallet OWNER TO ztn;

--
-- Name: headquarters_wallet_id_seq; Type: SEQUENCE; Schema: public; Owner: ztn
--

CREATE SEQUENCE public.headquarters_wallet_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.headquarters_wallet_id_seq OWNER TO ztn;

--
-- Name: headquarters_wallet_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ztn
--

ALTER SEQUENCE public.headquarters_wallet_id_seq OWNED BY public.headquarters_wallet.id;


--
-- Name: otp_codes; Type: TABLE; Schema: public; Owner: ztn
--

CREATE TABLE public.otp_codes (
    id integer NOT NULL,
    user_id integer NOT NULL,
    code character varying(6) NOT NULL,
    is_used boolean,
    created_at timestamp without time zone,
    expires_at timestamp without time zone NOT NULL,
    tenant_id integer NOT NULL
);


ALTER TABLE public.otp_codes OWNER TO ztn;

--
-- Name: otp_codes_id_seq; Type: SEQUENCE; Schema: public; Owner: ztn
--

CREATE SEQUENCE public.otp_codes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.otp_codes_id_seq OWNER TO ztn;

--
-- Name: otp_codes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ztn
--

ALTER SEQUENCE public.otp_codes_id_seq OWNED BY public.otp_codes.id;


--
-- Name: password_history; Type: TABLE; Schema: public; Owner: ztn
--

CREATE TABLE public.password_history (
    id integer NOT NULL,
    user_id integer NOT NULL,
    password_hash character varying(255) NOT NULL,
    created_at timestamp without time zone
);


ALTER TABLE public.password_history OWNER TO ztn;

--
-- Name: password_history_id_seq; Type: SEQUENCE; Schema: public; Owner: ztn
--

CREATE SEQUENCE public.password_history_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.password_history_id_seq OWNER TO ztn;

--
-- Name: password_history_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ztn
--

ALTER SEQUENCE public.password_history_id_seq OWNED BY public.password_history.id;


--
-- Name: pending_sim_swap; Type: TABLE; Schema: public; Owner: ztn
--

CREATE TABLE public.pending_sim_swap (
    id integer NOT NULL,
    token_hash character varying(128) NOT NULL,
    user_id integer NOT NULL,
    old_iccid character varying(32) NOT NULL,
    new_iccid character varying(32) NOT NULL,
    requested_by character varying(64),
    created_at timestamp without time zone,
    expires_at timestamp without time zone,
    is_verified boolean
);


ALTER TABLE public.pending_sim_swap OWNER TO ztn;

--
-- Name: pending_sim_swap_id_seq; Type: SEQUENCE; Schema: public; Owner: ztn
--

CREATE SEQUENCE public.pending_sim_swap_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.pending_sim_swap_id_seq OWNER TO ztn;

--
-- Name: pending_sim_swap_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ztn
--

ALTER SEQUENCE public.pending_sim_swap_id_seq OWNED BY public.pending_sim_swap.id;


--
-- Name: pending_transactions; Type: TABLE; Schema: public; Owner: ztn
--

CREATE TABLE public.pending_transactions (
    id integer NOT NULL,
    user_id integer NOT NULL,
    transaction_data text NOT NULL,
    transaction_type character varying(20) NOT NULL,
    created_at timestamp without time zone,
    expires_at timestamp without time zone NOT NULL,
    is_used boolean
);


ALTER TABLE public.pending_transactions OWNER TO ztn;

--
-- Name: pending_transactions_id_seq; Type: SEQUENCE; Schema: public; Owner: ztn
--

CREATE SEQUENCE public.pending_transactions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.pending_transactions_id_seq OWNER TO ztn;

--
-- Name: pending_transactions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ztn
--

ALTER SEQUENCE public.pending_transactions_id_seq OWNED BY public.pending_transactions.id;


--
-- Name: real_time_logs; Type: TABLE; Schema: public; Owner: ztn
--

CREATE TABLE public.real_time_logs (
    id integer NOT NULL,
    user_id integer,
    action character varying(1000) NOT NULL,
    "timestamp" timestamp without time zone,
    ip_address character varying(45),
    device_info character varying(200),
    location character varying(100),
    risk_alert boolean,
    tenant_id integer NOT NULL
);


ALTER TABLE public.real_time_logs OWNER TO ztn;

--
-- Name: real_time_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: ztn
--

CREATE SEQUENCE public.real_time_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.real_time_logs_id_seq OWNER TO ztn;

--
-- Name: real_time_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ztn
--

ALTER SEQUENCE public.real_time_logs_id_seq OWNED BY public.real_time_logs.id;


--
-- Name: sim_cards; Type: TABLE; Schema: public; Owner: ztn
--

CREATE TABLE public.sim_cards (
    id integer NOT NULL,
    iccid character varying(20) NOT NULL,
    mobile_number character varying(20) NOT NULL,
    network_provider character varying(50) NOT NULL,
    status character varying(20),
    registered_by character varying(100),
    registration_date timestamp without time zone,
    user_id integer
);


ALTER TABLE public.sim_cards OWNER TO ztn;

--
-- Name: sim_cards_id_seq; Type: SEQUENCE; Schema: public; Owner: ztn
--

CREATE SEQUENCE public.sim_cards_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.sim_cards_id_seq OWNER TO ztn;

--
-- Name: sim_cards_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ztn
--

ALTER SEQUENCE public.sim_cards_id_seq OWNED BY public.sim_cards.id;


--
-- Name: tenant_users; Type: TABLE; Schema: public; Owner: ztn
--

CREATE TABLE public.tenant_users (
    id integer NOT NULL,
    tenant_id integer NOT NULL,
    user_id integer NOT NULL,
    company_email character varying(120) NOT NULL,
    password_hash character varying(255) NOT NULL,
    created_at timestamp without time zone
);


ALTER TABLE public.tenant_users OWNER TO ztn;

--
-- Name: tenant_users_id_seq; Type: SEQUENCE; Schema: public; Owner: ztn
--

CREATE SEQUENCE public.tenant_users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.tenant_users_id_seq OWNER TO ztn;

--
-- Name: tenant_users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ztn
--

ALTER SEQUENCE public.tenant_users_id_seq OWNED BY public.tenant_users.id;


--
-- Name: tenants; Type: TABLE; Schema: public; Owner: ztn
--

CREATE TABLE public.tenants (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    api_key character varying(64) NOT NULL,
    contact_email character varying(120),
    plan character varying(50),
    created_at timestamp without time zone
);


ALTER TABLE public.tenants OWNER TO ztn;

--
-- Name: tenants_id_seq; Type: SEQUENCE; Schema: public; Owner: ztn
--

CREATE SEQUENCE public.tenants_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.tenants_id_seq OWNER TO ztn;

--
-- Name: tenants_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ztn
--

ALTER SEQUENCE public.tenants_id_seq OWNED BY public.tenants.id;


--
-- Name: transactions; Type: TABLE; Schema: public; Owner: ztn
--

CREATE TABLE public.transactions (
    id integer NOT NULL,
    user_id integer NOT NULL,
    amount double precision NOT NULL,
    transaction_type character varying(50) NOT NULL,
    status character varying(20),
    "timestamp" timestamp without time zone,
    location text,
    device_info text,
    fraud_flag boolean,
    risk_score double precision,
    transaction_metadata text,
    tenant_id integer NOT NULL
);


ALTER TABLE public.transactions OWNER TO ztn;

--
-- Name: transactions_id_seq; Type: SEQUENCE; Schema: public; Owner: ztn
--

CREATE SEQUENCE public.transactions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.transactions_id_seq OWNER TO ztn;

--
-- Name: transactions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ztn
--

ALTER SEQUENCE public.transactions_id_seq OWNED BY public.transactions.id;


--
-- Name: user_access_controls; Type: TABLE; Schema: public; Owner: ztn
--

CREATE TABLE public.user_access_controls (
    id integer NOT NULL,
    user_id integer NOT NULL,
    role_id integer NOT NULL,
    access_level character varying(20)
);


ALTER TABLE public.user_access_controls OWNER TO ztn;

--
-- Name: user_access_controls_id_seq; Type: SEQUENCE; Schema: public; Owner: ztn
--

CREATE SEQUENCE public.user_access_controls_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.user_access_controls_id_seq OWNER TO ztn;

--
-- Name: user_access_controls_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ztn
--

ALTER SEQUENCE public.user_access_controls_id_seq OWNED BY public.user_access_controls.id;


--
-- Name: user_auth_logs; Type: TABLE; Schema: public; Owner: ztn
--

CREATE TABLE public.user_auth_logs (
    id integer NOT NULL,
    user_id integer NOT NULL,
    auth_method character varying(50) NOT NULL,
    auth_status character varying(20),
    auth_timestamp timestamp without time zone,
    ip_address character varying(45),
    location character varying(100),
    device_info character varying(200),
    failed_attempts integer,
    geo_trust_score double precision,
    tenant_id integer NOT NULL
);


ALTER TABLE public.user_auth_logs OWNER TO ztn;

--
-- Name: user_auth_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: ztn
--

CREATE SEQUENCE public.user_auth_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.user_auth_logs_id_seq OWNER TO ztn;

--
-- Name: user_auth_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ztn
--

ALTER SEQUENCE public.user_auth_logs_id_seq OWNED BY public.user_auth_logs.id;


--
-- Name: user_roles; Type: TABLE; Schema: public; Owner: ztn
--

CREATE TABLE public.user_roles (
    id integer NOT NULL,
    role_name character varying(50) NOT NULL,
    permissions json,
    tenant_id integer
);


ALTER TABLE public.user_roles OWNER TO ztn;

--
-- Name: user_roles_id_seq; Type: SEQUENCE; Schema: public; Owner: ztn
--

CREATE SEQUENCE public.user_roles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.user_roles_id_seq OWNER TO ztn;

--
-- Name: user_roles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ztn
--

ALTER SEQUENCE public.user_roles_id_seq OWNED BY public.user_roles.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: ztn
--

CREATE TABLE public.users (
    id integer NOT NULL,
    identity_verified boolean,
    country character varying(50),
    trust_score double precision,
    last_login timestamp without time zone,
    created_at timestamp without time zone,
    password_hash character varying(255) NOT NULL,
    is_active boolean,
    first_name character varying(50) NOT NULL,
    last_name character varying(50),
    email character varying(120) NOT NULL,
    deletion_requested boolean,
    otp_secret character varying(32),
    otp_email_label character varying(120),
    locked_until timestamp without time zone,
    reset_token character varying(128),
    reset_token_expiry timestamp without time zone,
    tenant_id integer NOT NULL,
    is_tenant_admin boolean
);


ALTER TABLE public.users OWNER TO ztn;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: ztn
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_id_seq OWNER TO ztn;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ztn
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: wallets; Type: TABLE; Schema: public; Owner: ztn
--

CREATE TABLE public.wallets (
    id integer NOT NULL,
    user_id integer NOT NULL,
    balance double precision,
    currency character varying(10),
    last_transaction_at timestamp without time zone
);


ALTER TABLE public.wallets OWNER TO ztn;

--
-- Name: wallets_id_seq; Type: SEQUENCE; Schema: public; Owner: ztn
--

CREATE SEQUENCE public.wallets_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.wallets_id_seq OWNER TO ztn;

--
-- Name: wallets_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ztn
--

ALTER SEQUENCE public.wallets_id_seq OWNED BY public.wallets.id;


--
-- Name: webauthn_credentials; Type: TABLE; Schema: public; Owner: ztn
--

CREATE TABLE public.webauthn_credentials (
    id integer NOT NULL,
    user_id integer NOT NULL,
    credential_id bytea NOT NULL,
    public_key bytea NOT NULL,
    sign_count integer,
    transports character varying,
    created_at timestamp without time zone
);


ALTER TABLE public.webauthn_credentials OWNER TO ztn;

--
-- Name: webauthn_credentials_id_seq; Type: SEQUENCE; Schema: public; Owner: ztn
--

CREATE SEQUENCE public.webauthn_credentials_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.webauthn_credentials_id_seq OWNER TO ztn;

--
-- Name: webauthn_credentials_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ztn
--

ALTER SEQUENCE public.webauthn_credentials_id_seq OWNED BY public.webauthn_credentials.id;


--
-- Name: headquarters_wallet id; Type: DEFAULT; Schema: public; Owner: ztn
--

ALTER TABLE ONLY public.headquarters_wallet ALTER COLUMN id SET DEFAULT nextval('public.headquarters_wallet_id_seq'::regclass);


--
-- Name: otp_codes id; Type: DEFAULT; Schema: public; Owner: ztn
--

ALTER TABLE ONLY public.otp_codes ALTER COLUMN id SET DEFAULT nextval('public.otp_codes_id_seq'::regclass);


--
-- Name: password_history id; Type: DEFAULT; Schema: public; Owner: ztn
--

ALTER TABLE ONLY public.password_history ALTER COLUMN id SET DEFAULT nextval('public.password_history_id_seq'::regclass);


--
-- Name: pending_sim_swap id; Type: DEFAULT; Schema: public; Owner: ztn
--

ALTER TABLE ONLY public.pending_sim_swap ALTER COLUMN id SET DEFAULT nextval('public.pending_sim_swap_id_seq'::regclass);


--
-- Name: pending_transactions id; Type: DEFAULT; Schema: public; Owner: ztn
--

ALTER TABLE ONLY public.pending_transactions ALTER COLUMN id SET DEFAULT nextval('public.pending_transactions_id_seq'::regclass);


--
-- Name: real_time_logs id; Type: DEFAULT; Schema: public; Owner: ztn
--

ALTER TABLE ONLY public.real_time_logs ALTER COLUMN id SET DEFAULT nextval('public.real_time_logs_id_seq'::regclass);


--
-- Name: sim_cards id; Type: DEFAULT; Schema: public; Owner: ztn
--

ALTER TABLE ONLY public.sim_cards ALTER COLUMN id SET DEFAULT nextval('public.sim_cards_id_seq'::regclass);


--
-- Name: tenant_users id; Type: DEFAULT; Schema: public; Owner: ztn
--

ALTER TABLE ONLY public.tenant_users ALTER COLUMN id SET DEFAULT nextval('public.tenant_users_id_seq'::regclass);


--
-- Name: tenants id; Type: DEFAULT; Schema: public; Owner: ztn
--

ALTER TABLE ONLY public.tenants ALTER COLUMN id SET DEFAULT nextval('public.tenants_id_seq'::regclass);


--
-- Name: transactions id; Type: DEFAULT; Schema: public; Owner: ztn
--

ALTER TABLE ONLY public.transactions ALTER COLUMN id SET DEFAULT nextval('public.transactions_id_seq'::regclass);


--
-- Name: user_access_controls id; Type: DEFAULT; Schema: public; Owner: ztn
--

ALTER TABLE ONLY public.user_access_controls ALTER COLUMN id SET DEFAULT nextval('public.user_access_controls_id_seq'::regclass);


--
-- Name: user_auth_logs id; Type: DEFAULT; Schema: public; Owner: ztn
--

ALTER TABLE ONLY public.user_auth_logs ALTER COLUMN id SET DEFAULT nextval('public.user_auth_logs_id_seq'::regclass);


--
-- Name: user_roles id; Type: DEFAULT; Schema: public; Owner: ztn
--

ALTER TABLE ONLY public.user_roles ALTER COLUMN id SET DEFAULT nextval('public.user_roles_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: ztn
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Name: wallets id; Type: DEFAULT; Schema: public; Owner: ztn
--

ALTER TABLE ONLY public.wallets ALTER COLUMN id SET DEFAULT nextval('public.wallets_id_seq'::regclass);


--
-- Name: webauthn_credentials id; Type: DEFAULT; Schema: public; Owner: ztn
--

ALTER TABLE ONLY public.webauthn_credentials ALTER COLUMN id SET DEFAULT nextval('public.webauthn_credentials_id_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: ztn
--

COPY public.alembic_version (version_num) FROM stdin;
2ba407361fc1
\.


--
-- Data for Name: headquarters_wallet; Type: TABLE DATA; Schema: public; Owner: ztn
--

COPY public.headquarters_wallet (id, balance) FROM stdin;
1	499934000
\.


--
-- Data for Name: otp_codes; Type: TABLE DATA; Schema: public; Owner: ztn
--

COPY public.otp_codes (id, user_id, code, is_used, created_at, expires_at, tenant_id) FROM stdin;
1	22	329914	f	2025-03-28 09:15:53.865587	2025-03-28 09:20:53.863923	1
2	22	280651	f	2025-03-28 09:19:26.888727	2025-03-28 09:24:26.887348	1
48	22	416956	t	2025-04-01 07:04:20.128563	2025-04-01 07:09:20.127108	1
49	22	111625	t	2025-04-01 07:07:24.639577	2025-04-01 07:12:24.639089	1
50	22	309899	t	2025-04-01 07:09:53.783996	2025-04-01 07:14:53.782192	1
9	22	803320	f	2025-03-28 09:40:20.712957	2025-03-28 09:45:20.711552	1
10	22	570297	f	2025-03-28 09:41:53.615568	2025-03-28 09:46:53.615237	1
51	54	255515	t	2025-04-01 07:21:19.470666	2025-04-01 07:26:19.469112	1
52	22	776849	t	2025-04-01 07:39:13.306291	2025-04-01 07:44:13.305959	1
15	22	137464	f	2025-03-28 09:51:55.14444	2025-03-28 09:56:55.143046	1
16	22	161595	t	2025-03-28 10:06:21.515262	2025-03-28 10:11:21.514906	1
53	54	151277	t	2025-04-01 07:40:47.561009	2025-04-01 07:45:47.560665	1
54	55	530181	f	2025-04-01 07:44:40.696734	2025-04-01 07:49:40.696321	1
55	55	706642	f	2025-04-01 07:46:22.109804	2025-04-01 07:51:22.109378	1
19	22	219974	t	2025-03-28 10:43:50.676779	2025-03-28 10:48:50.675444	1
20	22	578156	t	2025-03-28 10:44:36.53288	2025-03-28 10:49:36.532554	1
56	22	980962	t	2025-04-01 07:47:38.837355	2025-04-01 07:52:38.836984	1
22	22	999551	t	2025-03-28 11:09:08.97284	2025-03-28 11:14:08.972505	1
57	55	203432	f	2025-04-01 07:49:45.287983	2025-04-01 07:54:45.287665	1
58	22	839331	t	2025-04-01 07:50:50.203937	2025-04-01 07:55:50.203624	1
59	55	815917	f	2025-04-01 07:51:52.768753	2025-04-01 07:56:52.768338	1
26	22	317316	t	2025-03-29 11:40:09.195286	2025-03-29 11:45:09.194952	1
60	22	171555	t	2025-04-01 07:54:28.902901	2025-04-01 07:59:28.902564	1
61	54	186865	t	2025-04-01 07:55:46.002963	2025-04-01 08:00:46.002643	1
62	55	157720	t	2025-04-01 07:58:25.504821	2025-04-01 08:03:25.504443	1
63	55	225751	t	2025-04-01 08:14:06.754949	2025-04-01 08:19:06.754629	1
31	22	230824	t	2025-03-29 11:47:40.272162	2025-03-29 11:52:40.271829	1
32	22	518986	t	2025-03-31 09:25:09.301448	2025-03-31 09:30:09.299938	1
64	55	160760	t	2025-04-01 08:32:32.197781	2025-04-01 08:37:32.197356	1
65	55	147492	t	2025-04-01 08:44:04.92364	2025-04-01 08:49:04.922262	1
66	22	666857	t	2025-04-01 09:29:52.392518	2025-04-01 09:34:52.39102	1
67	22	942839	t	2025-04-01 09:32:29.693868	2025-04-01 09:37:29.693449	1
68	22	548295	t	2025-04-01 09:49:12.145106	2025-04-01 09:54:12.144785	1
69	22	115903	t	2025-04-01 10:09:26.969714	2025-04-01 10:14:26.969297	1
70	22	573813	t	2025-04-01 10:35:11.174425	2025-04-01 10:40:11.173082	1
71	22	512758	t	2025-04-01 11:00:26.458971	2025-04-01 11:05:26.457423	1
42	22	169543	t	2025-04-01 05:52:45.183791	2025-04-01 05:57:45.183361	1
72	22	902334	t	2025-04-01 11:17:54.153923	2025-04-01 11:22:54.153581	1
73	22	905933	t	2025-04-01 11:38:12.357185	2025-04-01 11:43:12.35577	1
45	22	533198	t	2025-04-01 06:17:33.490231	2025-04-01 06:22:33.488711	1
46	22	543689	t	2025-04-01 06:21:01.507297	2025-04-01 06:26:01.506974	1
47	22	901205	t	2025-04-01 06:28:59.144437	2025-04-01 06:33:59.144107	1
74	22	725695	t	2025-04-01 11:54:55.638468	2025-04-01 11:59:55.636995	1
75	55	578141	t	2025-04-01 12:10:12.55102	2025-04-01 12:15:12.549899	1
76	54	608823	t	2025-04-01 12:14:03.579306	2025-04-01 12:19:03.57898	1
\.


--
-- Data for Name: password_history; Type: TABLE DATA; Schema: public; Owner: ztn
--

COPY public.password_history (id, user_id, password_hash, created_at) FROM stdin;
10	56	scrypt:32768:8:1$C7Dl4ChgZLzmSkRu$93604313dbc1fd3f3ecd38acf4ba09e31e249328015669197419aff32dea7a43b609e3de41d3091fe6337a4104220ac502afa28dc59b71308a316a9709be5b3b	2025-04-23 17:50:03.205524
11	56	scrypt:32768:8:1$kcnTWQyisPKKe6eB$062f8d5e277c12c336f98ba891f50859ccb6c0bfd2a9ea8f1e83022b06caa80bd70f311ceb19520ca13c94ec47978b0d0efadec04a20b30feab3b38e59cb6032	2025-04-24 09:55:13.860212
12	54	scrypt:32768:8:1$uzkPhThb9JGdUYVo$9f9bfb3423e365147a38f3812d039b618fa545ab02a518639c9e660edf862c7907abc9e89f292edd0dcc52d19bdf3418263c808ce8a38b7d2d3f008c521e256a	2025-04-25 11:02:39.077527
13	54	scrypt:32768:8:1$GVAmoCfQZZs1w7UG$87b73f0560bcc6256c23ea22db495b6519fd04e8b23ad8d93bd98cbf2111dd2fc3f035a256db0419b617bf79e005e009dad4ab98801a41c208eb7ef222d9cd3e	2025-04-25 11:38:09.374347
14	54	scrypt:32768:8:1$JXJDW1OZ0UgnhqOb$be354de47000b79bb659c70a15a72b19f8e2cc75d506454306ccb6166e5623569d0907a349d5938a9ad753ed4222c17f93c6fb47c5b9cf90562aa8ce261f4af4	2025-04-25 20:22:49.546125
15	22	scrypt:32768:8:1$TlIe6YcIj5auEJoK$02476cff4a81bf5b3f927f19d02d3279d13df63758a2a455390046e77954eb880de3d42f24175c5fe1a9f06f10b0b8825845010aec0cc6bc233b42d8d36dc6c7	2025-04-27 19:31:34.535713
16	56	scrypt:32768:8:1$Jf1vmvoJBhHFlHfx$af978acc09d77425f0b7ef23ce1475f3da1707aadadb8201a6749a63864a17507d92f04db905b5a65fbce875806698adec5764e4612ad51520fb0d818f2849b6	2025-04-30 16:36:13.220002
17	56	scrypt:32768:8:1$KQGM8HhBcmyPbCSF$693c5295ad89a82d0fa39873248f33556c36959688d86db8fa0dd25690d9965b00b6589cc1061cdd64a9663bc80148012c1af2e24e76e6eaab1376abc6a0599e	2025-05-02 13:28:35.28265
18	62	scrypt:32768:8:1$tncdMkxlZ9nfTxRP$36e4b56a19048ac21d48eb5577ad7aa2efb34cf8c1e602e5a90747256b17ef7e0f46ccf9f10f04942adfdfc3ecb101aa809416edb7758a714cfe0ebb423caeeb	2025-05-11 15:03:42.164559
19	56	scrypt:32768:8:1$OJWpX7mTpIOWdCl6$a1019c169683c1d9f0ba5a19278750e4220d14a359699c6d5775dd54013ad8002c2c31019a9513d747218b60a5cd7cbdbc8accb0bb7f829b2db47b66e5a66518	2025-05-12 17:31:03.447171
\.


--
-- Data for Name: pending_sim_swap; Type: TABLE DATA; Schema: public; Owner: ztn
--

COPY public.pending_sim_swap (id, token_hash, user_id, old_iccid, new_iccid, requested_by, created_at, expires_at, is_verified) FROM stdin;
1	8344b8d66ecbce8b10b600707e675d2bf1a65de56a2fff3150632cabd84f6a92	62	8901871711562650	8901669232128606	54	2025-05-07 10:11:41.060032	2025-05-07 10:26:41.058024	f
2	01dd0f3715f5207ece850297e6ec74a1a39477aa4eef0f52b927531a63b6c90a	62	8901871711562650	8901669232128606	54	2025-05-07 10:13:02.880188	2025-05-07 10:28:02.878667	f
3	de5fa6e24e3ce4b3cc8a30923bb02b7872c90c2a7725b3b300e60a338df370e2	62	8901871711562650	8901669232128606	54	2025-05-08 02:37:19.000935	2025-05-08 02:52:18.996042	f
4	8237b57a67b38f2c321294067319aada7aa908a7102d9cab42dcae0b93ec4920	62	8901871711562650	8901669232128606	54	2025-05-08 02:48:17.366963	2025-05-08 03:03:17.364158	f
5	fba01f7c9eebe5bba5c77ed003a304148324bbc66bb3797a479dd47141c7093a	62	8901871711562650	8901669232128606	54	2025-05-08 03:05:50.25456	2025-05-08 03:20:50.249967	f
6	7d3cd4498d641e42993ea51b1aa1856068d31617d64d1ca51904e4796793cbc3	62	8901871711562650	8901669232128606	54	2025-05-08 04:04:09.803443	2025-05-08 04:19:09.798806	f
7	c0c970df7491d61f4fd533cc289d7321d9019302229038f467eb6f4d35134244	62	8901871711562650	8901669232128606	54	2025-05-08 04:10:34.199942	2025-05-08 04:25:34.196849	f
8	5a8c6ac3596d26f556f2d2e20893b0990a4119458e32472b1c5b7ccd479c6052	62	8901871711562650	8901669232128606	54	2025-05-08 04:31:31.6304	2025-05-08 04:46:31.626701	f
9	7d9359b60b06d609a7d950e4ee8588dd12e452c4cb69c3c46e0bc1be24ffb5e6	62	8901871711562650	8901669232128606	54	2025-05-08 04:50:37.017567	2025-05-08 05:05:37.015508	f
10	2e85fe844aff0457992780af6ab2bf3b7655dec1703fa4c1399453c437abe5ea	62	8901871711562650	8901669232128606	54	2025-05-11 01:25:02.870509	2025-05-11 01:40:02.866198	f
11	fa1880e1c2eb7e26622fdc2d67e8218481ceb54b262e99cf64142ad521669acc	62	8901871711562650	8901669232128606	54	2025-05-11 01:41:49.470771	2025-05-11 01:56:49.468507	f
12	881a97ba0d53cf61cf495add3fab828561587a32afa0044efc0fb1a1269bd8ed	62	8901871711562650	8901669232128606	54	2025-05-11 01:59:01.53552	2025-05-11 02:14:01.533541	f
13	3da0afbdf052201dbc183e42f34903ed78f8ec6437d831dded59e42ab2156d28	62	8901871711562650	8901669232128606	54	2025-05-11 02:16:09.515498	2025-05-11 02:31:09.510763	f
14	a0b971296ed1962b6168b26b5416b6b4d57c9d4acb705576e3505acc10683f4d	62	8901871711562650	8901669232128606	54	2025-05-11 02:40:09.103854	2025-05-11 02:55:09.098689	f
15	32efff2edc9ea1746e7ae3ec879d812db32c0c2e1fd31b2c0832e6a56228ab3d	62	8901871711562650	8901669232128606	54	2025-05-11 02:57:34.108527	2025-05-11 03:12:34.105105	f
16	47d653fcf81ab155ee3a86dfd3ecbcc07afc4382d907fa30f7367d7fe18aa183	62	8901871711562650	8901669232128606	54	2025-05-11 03:13:38.959875	2025-05-11 03:28:38.957589	f
17	bf3558906146179d733102f44073789e391323d07eb504c199fd179c22d1e6ff	62	8901871711562650	8901669232128606	54	2025-05-11 03:29:58.328229	2025-05-11 03:44:58.324534	f
19	b9af57a0b1ce204bd650f788b82dbacb6c684005037f5424041e05ce3fc64448	70	8901839465275236	8901909162366461	54	2025-05-12 08:24:32.785146	2025-05-12 08:39:32.779621	f
\.


--
-- Data for Name: pending_transactions; Type: TABLE DATA; Schema: public; Owner: ztn
--

COPY public.pending_transactions (id, user_id, transaction_data, transaction_type, created_at, expires_at, is_used) FROM stdin;
\.


--
-- Data for Name: real_time_logs; Type: TABLE DATA; Schema: public; Owner: ztn
--

COPY public.real_time_logs (id, user_id, action, "timestamp", ip_address, device_info, location, risk_alert, tenant_id) FROM stdin;
1451	22	✅ Successful login	2025-04-26 14:27:41.758184	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1477	57	✅ Successful login	2025-04-26 21:53:15.826154	127.0.0.1	IAMaaS API Access	Unknown	f	3
1478	57	✅ Successful login	2025-04-26 21:56:09.853146	127.0.0.1	IAMaaS API Access	Unknown	f	2
1479	57	✅ Successful login	2025-04-26 21:56:34.412565	127.0.0.1	IAMaaS API Access	Unknown	f	2
1480	57	✅ Successful login	2025-04-26 21:59:11.817181	127.0.0.1	IAMaaS API Access	Unknown	f	2
1481	57	✅ Successful login	2025-04-26 22:09:46.442527	127.0.0.1	IAMaaS API Access	Unknown	f	2
1482	57	✅ Successful login	2025-04-26 22:15:44.574756	127.0.0.1	IAMaaS API Access	Unknown	f	2
1483	57	✅ Successful login	2025-04-26 22:23:36.878658	127.0.0.1	IAMaaS API Access	Unknown	f	2
1484	57	✅ Successful login	2025-04-26 22:28:18.496373	127.0.0.1	IAMaaS API Access	Unknown	f	2
1485	57	✅ Successful login	2025-04-26 22:35:35.215535	127.0.0.1	IAMaaS API Access	Unknown	f	2
1486	57	✅ Successful login	2025-04-26 22:50:33.276548	127.0.0.1	IAMaaS API Access	Unknown	f	2
1491	56	✅ Successful login	2025-04-27 18:34:14.32898	127.0.0.1	IAMaaS API Access	Unknown	f	2
1544	54	✅ Successful login	2025-04-28 10:22:53.195527	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1545	54	✅ TOTP verified successfully	2025-04-28 10:23:37.702615	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1546	54	🔐 Logged in via WebAuthn (USB security key)	2025-04-28 10:24:21.759636	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1549	54	❌ Failed login: Invalid password (2)	2025-04-28 10:38:41.95163	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
1559	22	✅ Successful login	2025-04-30 15:43:38.246666	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1560	22	✅ TOTP verified successfully	2025-04-30 15:43:55.668771	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1561	22	🔐 Logged in via WebAuthn (USB security key)	2025-04-30 15:44:36.169077	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1562	54	❌ Failed login: Invalid password (1)	2025-04-30 15:47:21.239361	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	Unknown	f	1
1564	54	❌ Failed login: Invalid password (3)	2025-04-30 15:47:24.079334	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	Unknown	t	1
1566	54	❌ Failed login: Invalid password (5)	2025-04-30 15:47:27.40889	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	Unknown	t	1
1567	54	🚨 Account temporarily locked due to failed login attempts	2025-04-30 15:47:27.40889	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	Unknown	t	1
1606	69	✅ Successful login	2025-05-02 11:42:17.457601	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1607	69	✅ TOTP verified successfully	2025-05-02 11:42:38.637181	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1608	69	🔐 Logged in via WebAuthn (cross-device passkey)	2025-05-02 11:43:08.000875	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1609	54	❌ Failed login: Invalid password (1)	2025-05-02 11:46:14.857823	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1611	54	✅ TOTP verified successfully	2025-05-02 11:46:39.800112	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1612	54	🔐 Logged in via WebAuthn (USB security key)	2025-05-02 11:47:20.518534	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1666	56	❌ Failed login: Invalid password (1)	2025-05-03 20:43:53.420264	192.168.60.3	Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0	Unknown	f	1
1667	56	✅ Successful login	2025-05-03 20:44:11.89617	192.168.60.3	Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0	Unknown	f	1
1668	56	✅ TOTP verified successfully	2025-05-03 20:44:37.43287	192.168.60.3	Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0	Unknown	f	1
1669	56	⚠️ Client-side WebAuthn failure: WebAuthn blocked due to insecure context or permissions. (SecurityError: The operation is insecure.)	2025-05-03 20:44:38.056812	192.168.60.3	Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0	Unknown	f	1
1670	56	⚠️ Client-side WebAuthn failure: WebAuthn blocked due to insecure context or permissions. (SecurityError: The operation is insecure.)	2025-05-03 20:45:43.142609	192.168.60.3	Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0	Unknown	f	1
1671	56	⚠️ Client-side WebAuthn failure: WebAuthn blocked due to insecure context or permissions. (SecurityError: The operation is insecure.)	2025-05-03 20:45:44.045747	192.168.60.3	Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0	Unknown	f	1
1672	54	❌ Failed login: Invalid password (1)	2025-05-03 20:48:07.019231	192.168.60.7	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1673	54	✅ Successful login	2025-05-03 20:48:10.910136	192.168.60.7	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1674	54	✅ TOTP verified successfully	2025-05-03 20:48:22.621954	192.168.60.7	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1675	54	⚠️ Client-side WebAuthn failure: WebAuthn blocked due to insecure context or permissions. (SecurityError: This is an invalid domain.)	2025-05-03 20:48:23.256707	192.168.60.7	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1775	22	✅ Successful login	2025-05-05 10:38:25.355293	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1776	22	✅ TOTP verified successfully	2025-05-05 10:38:41.843997	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1777	22	🔐 Logged in via WebAuthn (USB security key)	2025-05-05 10:39:08.388829	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1778	22	✅ Successful login	2025-05-05 11:19:08.546317	192.168.2.116	Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0	Unknown	f	1
1453	22	✅ TOTP verified successfully	2025-04-26 14:32:37.84901	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1487	57	✅ Successful login	2025-04-26 23:03:06.294382	127.0.0.1	IAMaaS API Access	Unknown	f	2
1488	58	✅ Successful login	2025-04-26 23:05:28.768252	127.0.0.1	IAMaaS API Access	Unknown	f	2
1489	56	🆕 IAMaaS User Registered via API (Mobile 0783437740)	2025-04-26 23:16:08.369086	127.0.0.1	IAMaaS API	Unknown	f	2
1490	56	✅ Successful login	2025-04-26 23:18:09.629597	127.0.0.1	IAMaaS API Access	Unknown	f	2
1492	56	✅ Successful login	2025-04-27 19:01:08.341662	127.0.0.1	IAMaaS API Access	Unknown	f	2
1493	56	✅ Successful login	2025-04-27 19:01:59.348842	127.0.0.1	IAMaaS API Access	Unknown	f	2
1494	56	✅ Successful login	2025-04-27 19:06:30.396995	127.0.0.1	IAMaaS API Access	Unknown	f	2
1495	54	❌ Failed login: Invalid password (1)	2025-04-27 19:12:28.795755	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
1496	54	❌ Failed login: Invalid password (2)	2025-04-27 19:12:36.785175	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
1497	54	✅ Successful login	2025-04-27 19:12:47.844923	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
1498	54	✅ TOTP verified successfully	2025-04-27 19:13:06.603166	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
1499	54	🔐 Logged in via WebAuthn (USB security key)	2025-04-27 19:13:42.944035	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
1500	56	❌ Failed login: Invalid password (1)	2025-04-27 19:14:29.32411	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1509	22	❌ Failed login: Invalid password (2)	2025-04-27 19:20:59.055582	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1514	22	📧 Password reset requested	2025-04-27 19:25:10.866392	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1515	54	❌ Failed login: Invalid password (3)	2025-04-27 19:29:52.572176	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
1520	22	✅ Successful login	2025-04-27 19:46:23.597566	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1522	22	🔐 Logged in via WebAuthn (USB security key)	2025-04-27 19:46:47.408822	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1547	22	📧 Password reset requested	2025-04-28 10:33:53.537328	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1551	54	❌ Failed login: Invalid password (4)	2025-04-28 10:38:43.363105	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
1555	22	✅ TOTP verified successfully	2025-04-28 10:39:38.998302	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1556	22	🔐 Logged in via WebAuthn (USB security key)	2025-04-28 10:39:44.890476	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1563	54	❌ Failed login: Invalid password (2)	2025-04-30 15:47:22.649783	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	Unknown	f	1
1565	54	❌ Failed login: Invalid password (4)	2025-04-30 15:47:25.884575	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	Unknown	t	1
1610	54	✅ Successful login	2025-05-02 11:46:26.159881	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1676	22	✅ Successful login	2025-05-03 21:38:57.914478	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0	Unknown	f	1
1677	22	❌ Failed TOTP verification (1)	2025-05-03 21:39:25.342776	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0	Unknown	t	1
1678	22	✅ TOTP verified successfully	2025-05-03 21:39:47.414061	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0	Unknown	f	1
1679	22	⚠️ Client-side WebAuthn failure: WebAuthn blocked due to insecure context or permissions. (SecurityError: The operation is insecure.)	2025-05-03 21:39:48.050422	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0	Unknown	f	1
1680	22	⚠️ Client-side WebAuthn failure: WebAuthn blocked due to insecure context or permissions. (SecurityError: The operation is insecure.)	2025-05-03 21:40:38.106678	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0	Unknown	f	1
1681	22	✅ Successful login	2025-05-03 21:46:30.988519	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1682	22	✅ TOTP verified successfully	2025-05-03 21:46:54.030896	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1683	22	⚠️ Client-side WebAuthn failure: WebAuthn blocked due to insecure context or permissions. (SecurityError: The relying party ID is not a registrable domain suffix of, nor equal to the current domain. Subsequently, an attempt to fetch the .well-known/webauthn resource of the claimed RP ID failed.)	2025-05-03 21:46:54.745008	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1779	22	✅ TOTP verified successfully	2025-05-05 11:19:27.607634	192.168.2.116	Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0	Unknown	f	1
1780	22	🔐 Logged in via WebAuthn (USB security key)	2025-05-05 11:19:33.919558	192.168.2.116	Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0	Unknown	f	1
1782	22	💸 Funded agent bztn (0784690255) with 1000.0 RWF from HQ Wallet	2025-05-05 11:24:52.942713	192.168.2.116	Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0	{"lat": 35.6916, "lng": 139.768}	f	1
1783	22	✅ Successful login	2025-05-05 11:36:13.784218	192.168.2.116	Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0	Unknown	f	1
1785	22	✅ TOTP verified successfully	2025-05-05 11:36:43.194893	192.168.2.116	Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0	Unknown	f	1
1786	22	🔐 Logged in via WebAuthn (USB security key)	2025-05-05 11:36:48.746354	192.168.2.116	Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0	Unknown	f	1
1787	54	✅ Successful login	2025-05-05 11:51:14.03646	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1794	22	✅ TOTP verified successfully	2025-05-05 12:02:10.774086	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	Unknown	f	1
1454	22	✅ Successful login	2025-04-26 14:44:11.928301	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1455	22	✅ TOTP verified successfully	2025-04-26 14:44:27.143102	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1456	22	🔐 Logged in via WebAuthn (USB security key)	2025-04-26 14:44:32.545087	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1458	54	❌ Failed login: Invalid password (2)	2025-04-26 14:46:07.361276	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1460	54	✅ TOTP verified successfully	2025-04-26 14:46:37.369804	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1461	54	🔐 Logged in via WebAuthn (USB security key)	2025-04-26 14:46:42.665233	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1463	59	❌ Failed TOTP verification (1)	2025-04-26 14:47:47.005951	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1501	56	❌ Failed login: Invalid password (2)	2025-04-27 19:14:42.430352	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1510	22	❌ Failed login: Invalid password (3)	2025-04-27 19:22:40.639793	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1516	54	✅ Successful login	2025-04-27 19:30:06.502055	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
1518	54	🔐 Logged in via WebAuthn (USB security key)	2025-04-27 19:30:54.536707	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
1519	22	✅ Password reset after MFA and checks	2025-04-27 19:31:34.535713	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
1548	54	❌ Failed login: Invalid password (1)	2025-04-28 10:38:40.754004	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
1552	54	❌ Failed login: Invalid password (5)	2025-04-28 10:38:44.077104	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
1553	54	🚨 Account temporarily locked due to failed login attempts	2025-04-28 10:38:44.077104	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
1568	22	✅ Successful login	2025-04-30 16:27:15.84037	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1569	22	✅ TOTP verified successfully	2025-04-30 16:28:44.054254	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1570	22	🔐 Logged in via WebAuthn (USB security key)	2025-04-30 16:30:12.666923	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1573	56	📧 Password reset requested	2025-04-30 16:34:44.588319	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1575	61	❌ Failed login: Invalid password (1)	2025-04-30 16:37:54.298926	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1577	\N	❌ Failed login: Unknown identifier 07867832379	2025-04-30 16:38:43.862353	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1579	54	✅ TOTP verified successfully	2025-04-30 16:39:38.143924	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1580	54	🔐 Logged in via WebAuthn (USB security key)	2025-04-30 16:39:46.726083	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1614	54	✅ Successful login	2025-05-02 12:08:52.718301	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1615	54	✅ TOTP verified successfully	2025-05-02 12:09:09.674025	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1616	54	🔐 Logged in via WebAuthn (USB security key)	2025-05-02 12:09:14.642298	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1684	22	✅ Successful login	2025-05-03 22:13:38.424913	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0	Unknown	f	1
1685	22	✅ TOTP verified successfully	2025-05-03 22:14:27.938796	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0	Unknown	f	1
1686	22	⚠️ Client-side WebAuthn failure: User cancelled or did not interact with WebAuthn prompt in time. (NotAllowedError: The request is not allowed by the user agent or the platform in the current context, possibly because the user denied permission.)	2025-05-03 22:14:43.677718	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0	Unknown	f	1
1687	22	⚠️ Client-side WebAuthn failure: User cancelled or did not interact with WebAuthn prompt in time. (NotAllowedError: The request is not allowed by the user agent or the platform in the current context, possibly because the user denied permission.)	2025-05-03 22:15:05.180608	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0	Unknown	f	1
1688	22	⚠️ Client-side WebAuthn failure: User cancelled or did not interact with WebAuthn prompt in time. (NotAllowedError: The request is not allowed by the user agent or the platform in the current context, possibly because the user denied permission.)	2025-05-03 22:15:45.733605	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0	Unknown	f	1
1781	22	📱 Admin generated SIM: 8901898354917681 with mobile 0787609027	2025-05-05 11:20:59.728874	192.168.2.116	Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0	Headquarters	f	1
1784	22	❌ Failed TOTP verification (1)	2025-05-05 11:36:30.036797	192.168.2.116	Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0	Unknown	t	1
1788	54	✅ TOTP verified successfully	2025-05-05 11:51:28.014857	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1789	54	🔐 Logged in via WebAuthn (USB security key)	2025-05-05 11:51:45.544415	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1796	54	✅ Successful login	2025-05-05 12:28:05.873693	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	Unknown	f	1
1798	54	🔐 Logged in via WebAuthn (USB security key)	2025-05-05 12:28:25.653092	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	Unknown	f	1
1457	54	❌ Failed login: Invalid password (1)	2025-04-26 14:45:55.99506	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1459	54	✅ Successful login	2025-04-26 14:46:12.377917	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1462	59	✅ Successful login	2025-04-26 14:47:09.930462	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1502	56	❌ Failed login: Invalid password (3)	2025-04-27 19:15:03.013381	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1506	\N	❌ Failed login: Unknown identifier patrick.mutabazi.pj1@g.ext.naist.j	2025-04-27 19:18:47.573643	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1517	54	✅ TOTP verified successfully	2025-04-27 19:30:48.195287	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
1521	22	✅ TOTP verified successfully	2025-04-27 19:46:40.656636	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1550	54	❌ Failed login: Invalid password (3)	2025-04-28 10:38:42.696302	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
1554	22	✅ Successful login	2025-04-28 10:39:15.980676	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1558	56	✅ Successful login	2025-04-28 10:57:58.517799	127.0.0.1	IAMaaS API Access	Unknown	f	2
1574	56	✅ Password reset after MFA and checks	2025-04-30 16:36:13.220002	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1576	61	❌ Failed login: Invalid password (2)	2025-04-30 16:38:01.962307	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1578	54	✅ Successful login	2025-04-30 16:39:22.269227	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1689	22	✅ Successful login	2025-05-03 22:18:52.592977	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1690	22	✅ TOTP verified successfully	2025-05-03 22:19:07.004002	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1691	22	🔐 Logged in via WebAuthn (USB security key)	2025-05-03 22:19:13.407731	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1692	22	⚠️ Client-side WebAuthn failure: User cancelled or did not interact with WebAuthn prompt in time. (NotAllowedError: The request is not allowed by the user agent or the platform in the current context, possibly because the user denied permission.)	2025-05-03 22:24:16.005988	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0	Unknown	f	1
1790	54	✅ Successful login	2025-05-05 11:53:51.402211	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	Unknown	f	1
1792	54	🔐 Logged in via WebAuthn (USB security key)	2025-05-05 11:54:14.208632	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	Unknown	f	1
1793	22	✅ Successful login	2025-05-05 12:01:52.65242	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	Unknown	f	1
1795	22	🔐 Logged in via WebAuthn (USB security key)	2025-05-05 12:02:16.892367	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	Unknown	f	1
1464	59	❌ Failed TOTP verification (2)	2025-04-26 14:48:09.215732	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1503	56	❌ Failed login: Invalid password (4)	2025-04-27 19:15:05.67518	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1507	\N	❌ Failed login: Unknown identifier patrick.mutabazi.pj1@g.ext.naist.jp	2025-04-27 19:18:53.209301	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1511	22	❌ Failed login: Invalid password (4)	2025-04-27 19:24:16.281676	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1582	56	✅ Successful login	2025-04-30 16:48:54.15291	127.0.0.1	IAMaaS API Access	Unknown	f	2
1583	54	✅ TOTP verified successfully	2025-04-30 16:51:19.968422	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1584	54	📨 TOTP reset link requested	2025-04-30 16:52:11.079127	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1585	54	✅ TOTP reset after identity + trust check	2025-04-30 16:53:01.521263	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1586	54	✅ Successful login	2025-04-30 16:53:41.918299	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1587	54	✅ TOTP verified successfully	2025-04-30 16:54:38.631605	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1588	54	🔐 Logged in via WebAuthn (USB security key)	2025-04-30 16:54:45.26679	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1618	54	✅ Successful login	2025-05-02 12:25:19.865623	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1619	54	✅ TOTP verified successfully	2025-05-02 12:25:39.929707	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1620	54	🔐 Logged in via WebAuthn (USB security key)	2025-05-02 12:25:44.762645	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1693	22	✅ Successful login	2025-05-03 22:32:39.080221	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1694	22	✅ TOTP verified successfully	2025-05-03 22:32:51.430501	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1695	22	🔐 Logged in via WebAuthn (USB security key)	2025-05-03 22:32:57.03249	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1791	54	✅ TOTP verified successfully	2025-05-05 11:54:09.081705	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	Unknown	f	1
1797	54	✅ TOTP verified successfully	2025-05-05 12:28:21.06053	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	Unknown	f	1
1465	22	✅ Successful login	2025-04-26 16:11:39.44935	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1466	22	✅ TOTP verified successfully	2025-04-26 16:11:58.480708	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1467	22	🔐 Logged in via WebAuthn (USB security key)	2025-04-26 16:12:04.446236	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1504	56	❌ Failed login: Invalid password (5)	2025-04-27 19:15:06.699079	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1505	56	🚨 Account temporarily locked due to failed login attempts	2025-04-27 19:15:06.699079	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1508	22	❌ Failed login: Invalid password (1)	2025-04-27 19:20:30.927032	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1512	22	❌ Failed login: Invalid password (5)	2025-04-27 19:24:26.730792	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1513	22	🚨 Account temporarily locked due to failed login attempts	2025-04-27 19:24:26.730792	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1589	54	✅ Successful login	2025-04-30 17:04:00.380061	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	Unknown	f	1
1621	54	🧾 Agent deposited 1000.0 RWF to bztn (0784690255)	2025-05-02 12:26:10.09378	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	34.7315, 135.7347	f	1
1623	69	✅ TOTP verified successfully	2025-05-02 12:26:57.863895	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1696	22	✅ TOTP verified successfully	2025-05-03 22:43:09.99136	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1697	22	🔐 Logged in via WebAuthn (USB security key)	2025-05-03 22:43:15.218143	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1799	54	✅ Successful login	2025-05-05 12:54:34.756197	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	Unknown	f	1
1800	54	✅ TOTP verified successfully	2025-05-05 12:54:56.889987	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	Unknown	f	1
1801	54	🔐 Logged in via WebAuthn (USB security key)	2025-05-05 12:55:02.009143	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	Unknown	f	1
1	55	⚠️ Suspicious transfer of 100,000 RWF flagged (manual test)	2025-04-07 11:22:24.89784	192.168.1.99	TestBrowser/9.1	Kigali	t	1
1468	57	🆕 IAMaaS User Registered via API (Mobile 0787408913)	2025-04-26 17:02:05.504165	127.0.0.1	IAMaaS API	Unknown	f	2
1469	58	❌ Failed login: User not under tenant	2025-04-26 17:05:09.570216	127.0.0.1	IAMaaS API Access	Unknown	t	2
1470	58	🆕 IAMaaS User Registered via API (Mobile 0787195372)	2025-04-26 17:05:42.310556	127.0.0.1	IAMaaS API	Unknown	f	2
1471	58	✅ Successful login	2025-04-26 17:06:08.395846	127.0.0.1	IAMaaS API Access	Unknown	f	2
1472	57	🆕 IAMaaS User Registered via API (Mobile 0787408913)	2025-04-26 17:10:02.895835	127.0.0.1	IAMaaS API	Unknown	f	3
1473	57	🆕 IAMaaS User Registered via API (Mobile 0787408913)	2025-04-26 17:11:36.005251	127.0.0.1	IAMaaS API	Unknown	f	3
1528	22	✅ Successful login	2025-04-27 20:18:46.618513	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1529	22	📨 TOTP reset link requested	2025-04-27 20:18:54.889243	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1530	22	✅ TOTP reset after identity + trust check	2025-04-27 20:19:57.333046	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1531	22	✅ Successful login	2025-04-27 20:20:14.00674	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1532	22	✅ Successful login	2025-04-27 20:36:27.587038	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1533	22	❌ Failed TOTP verification (1)	2025-04-27 20:37:32.280232	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1534	22	✅ TOTP verified successfully	2025-04-27 20:37:44.719592	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1535	22	🔐 Logged in via WebAuthn (USB security key)	2025-04-27 20:37:53.03271	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1590	54	✅ TOTP verified successfully	2025-04-30 17:04:20.109015	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	Unknown	f	1
1622	69	✅ Successful login	2025-05-02 12:26:43.903429	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1624	69	🔐 Logged in via WebAuthn (USB security key)	2025-05-02 12:27:08.075824	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1698	54	❌ Failed login: Invalid password (2)	2025-05-03 22:44:05.770984	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1699	54	✅ Successful login	2025-05-03 22:44:10.462517	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1700	54	✅ TOTP verified successfully	2025-05-03 22:44:22.780761	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1701	54	🔐 Logged in via WebAuthn (USB security key)	2025-05-03 22:44:27.919292	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1702	22	✅ Successful login	2025-05-03 22:45:08.460592	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1704	22	🔐 Logged in via WebAuthn (USB security key)	2025-05-03 22:45:24.848086	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1707	22	✅ Successful login	2025-05-03 22:47:30.586056	192.168.60.3	Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0	Unknown	f	1
1710	22	✅ TOTP verified successfully	2025-05-03 22:58:06.462811	192.168.60.3	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1712	22	⚠️ Client-side WebAuthn failure: User cancelled or did not interact with WebAuthn prompt in time. (NotAllowedError: WebAuthn is not supported on sites with TLS certificate errors.)	2025-05-03 22:58:18.766036	192.168.60.3	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1718	22	✅ TOTP verified successfully	2025-05-03 22:59:15.64037	192.168.60.3	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1720	22	⚠️ Client-side WebAuthn failure: User cancelled or did not interact with WebAuthn prompt in time. (NotAllowedError: WebAuthn is not supported on sites with TLS certificate errors.)	2025-05-03 22:59:57.992033	192.168.60.3	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1726	22	✅ TOTP verified successfully	2025-05-03 23:01:15.599446	192.168.60.3	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1729	22	✅ TOTP verified successfully	2025-05-03 23:02:08.366055	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1732	22	✅ TOTP verified successfully	2025-05-03 23:22:55.751439	192.168.60.3	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1742	22	✅ TOTP verified successfully	2025-05-04 00:00:52.335919	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1746	56	❌ Failed login: Invalid password (3)	2025-05-04 00:20:04.468049	192.168.60.3	curl/8.13.0	Unknown	t	1
1754	\N	❌ Failed login: Unknown identifier 0781617617	2025-05-04 00:22:41.260887	192.168.60.3	python-requests/2.32.3	Unknown	t	1
1757	\N	❌ Failed login: Unknown identifier 0781617617	2025-05-04 00:36:50.611752	192.168.60.3	python-requests/2.32.3	Unknown	t	1
1762	56	❌ Failed login: Invalid password (6)	2025-05-04 00:42:07.153095	192.168.60.3	python-requests/2.32.3	Unknown	t	1
1763	56	🚨 Account temporarily locked due to failed login attempts	2025-05-04 00:42:07.153095	192.168.60.3	python-requests/2.32.3	Unknown	t	1
1767	\N	❌ Failed login: Unknown identifier 0781617617	2025-05-04 00:42:17.059895	192.168.60.3	python-requests/2.32.3	Unknown	t	1
1772	22	✅ TOTP verified successfully	2025-05-04 00:46:56.013989	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1774	22	⚠️ Client-side WebAuthn failure: User cancelled or did not interact with WebAuthn prompt in time. (NotAllowedError: The operation either timed out or was not allowed. See: https://www.w3.org/TR/webauthn-2/#sctn-privacy-considerations-client.)	2025-05-04 00:48:41.058473	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1802	54	✅ Successful login	2025-05-05 13:12:04.588937	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	Unknown	f	1
1474	58	❌ Failed login: User not under tenant	2025-04-26 17:27:39.820348	127.0.0.1	IAMaaS API Access	Unknown	t	3
1475	57	✅ Successful login	2025-04-26 17:28:16.070724	127.0.0.1	IAMaaS API Access	Unknown	f	3
1536	54	❌ Failed login: Invalid password (4)	2025-04-27 21:27:22.568236	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1537	54	✅ Successful login	2025-04-27 21:27:29.210481	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1538	54	📨 TOTP reset link requested	2025-04-27 21:27:39.9908	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1539	54	✅ TOTP reset after identity + trust check	2025-04-27 21:28:48.879168	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1540	54	✅ Successful login	2025-04-27 21:29:07.201637	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1541	54	✅ Successful login	2025-04-27 21:30:17.509243	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1542	54	✅ TOTP verified successfully	2025-04-27 21:41:11.728423	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1543	54	🔐 Logged in via WebAuthn (USB security key)	2025-04-27 21:41:17.891245	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1591	69	🆕 New user registered using ICCID 8901765884990587 (SIM created by: 54)	2025-04-30 18:13:49.434582	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
1592	69	❌ Failed login: Invalid password (1)	2025-04-30 18:14:12.872761	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
1593	69	✅ Successful login	2025-04-30 18:14:20.315034	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
1626	69	Withdrawal of 200.0 RWF	2025-05-02 12:33:43.733826	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	34.7315, 135.7347	f	1
1629	54	❌ Failed login: Invalid password (3)	2025-05-02 12:35:58.019849	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	t	1
1631	54	✅ TOTP verified successfully	2025-05-02 12:36:19.899927	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1632	54	🔐 Logged in via WebAuthn (USB security key)	2025-05-02 12:36:25.304769	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1636	22	🔐 Logged in via WebAuthn (USB security key)	2025-05-02 12:38:20.075652	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1703	22	✅ TOTP verified successfully	2025-05-03 22:45:20.172998	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1705	22	📱 Admin generated SIM: 8901906398734427 with mobile 0787280664	2025-05-03 22:45:57.459323	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Headquarters	f	1
1708	22	✅ TOTP verified successfully	2025-05-03 22:47:44.643451	192.168.60.3	Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0	Unknown	f	1
1723	22	⚠️ Client-side WebAuthn failure: User cancelled or did not interact with WebAuthn prompt in time. (NotAllowedError: WebAuthn is not supported on sites with TLS certificate errors.)	2025-05-03 23:00:01.469437	192.168.60.3	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1741	22	✅ Successful login	2025-05-04 00:00:37.176591	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1745	69	✅ Successful login	2025-05-04 00:14:00.634423	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1753	\N	❌ Failed login: Unknown identifier 0781617617	2025-05-04 00:22:40.996305	192.168.60.3	python-requests/2.32.3	Unknown	t	1
1756	\N	❌ Failed login: Unknown identifier 0781617617	2025-05-04 00:36:50.304868	192.168.60.3	python-requests/2.32.3	Unknown	t	1
1761	\N	❌ Failed login: Unknown identifier 0781617617	2025-05-04 00:36:51.841208	192.168.60.3	python-requests/2.32.3	Unknown	t	1
1766	\N	❌ Failed login: Unknown identifier 0781617617	2025-05-04 00:42:16.750797	192.168.60.3	python-requests/2.32.3	Unknown	t	1
1771	22	✅ Successful login	2025-05-04 00:46:04.284604	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1803	54	✅ TOTP verified successfully	2025-05-05 13:12:23.197688	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	Unknown	f	1
1804	54	🔐 Logged in via WebAuthn (USB security key)	2025-05-05 13:12:28.536333	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	Unknown	f	1
1476	57	✅ Successful login	2025-04-26 18:35:34.103292	127.0.0.1	IAMaaS API Access	Unknown	f	3
1594	22	✅ Successful login	2025-04-30 18:30:42.606044	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1595	22	✅ TOTP verified successfully	2025-04-30 18:31:09.756898	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1596	22	🔐 Logged in via WebAuthn (USB security key)	2025-04-30 18:31:15.903353	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1627	69	Transfer of 100.0 RWF	2025-05-02 12:35:12.034113	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	34.7315, 135.7347	f	1
1628	54	❌ Failed login: Invalid password (2)	2025-05-02 12:35:50.68333	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1630	54	✅ Successful login	2025-05-02 12:36:02.849575	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1635	22	✅ TOTP verified successfully	2025-05-02 12:38:15.267985	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1706	22	❌ Failed login: Invalid password (1)	2025-05-03 22:47:16.817638	192.168.60.3	Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0	Unknown	f	1
1709	22	✅ Successful login	2025-05-03 22:57:45.283834	192.168.60.3	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1714	22	⚠️ Client-side WebAuthn failure: User cancelled or did not interact with WebAuthn prompt in time. (NotAllowedError: WebAuthn is not supported on sites with TLS certificate errors.)	2025-05-03 22:58:21.98887	192.168.60.3	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1717	22	❌ Failed TOTP verification (3)	2025-05-03 22:59:00.955599	192.168.60.3	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	t	1
1722	22	⚠️ Client-side WebAuthn failure: User cancelled or did not interact with WebAuthn prompt in time. (NotAllowedError: WebAuthn is not supported on sites with TLS certificate errors.)	2025-05-03 22:59:59.834561	192.168.60.3	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1725	22	✅ Successful login	2025-05-03 23:01:01.256211	192.168.60.3	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1728	22	✅ Successful login	2025-05-03 23:01:52.990234	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1730	22	🔐 Logged in via WebAuthn (USB security key)	2025-05-03 23:02:15.521621	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1731	22	✅ Successful login	2025-05-03 23:22:25.961943	192.168.60.3	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1734	22	🔐 Logged in via WebAuthn (cross-device passkey)	2025-05-03 23:27:19.080859	192.168.60.3	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1735	22	👁️ Viewed profile of Mamure Malakai (0782858063)	2025-05-03 23:27:51.536164	192.168.60.3	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Headquarters	f	1
1740	56	❌ Failed login: Invalid password (2)	2025-05-03 23:59:58.568801	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1743	22	⚠️ Client-side WebAuthn failure: User cancelled or did not interact with WebAuthn prompt in time. (NotAllowedError: The operation either timed out or was not allowed. See: https://www.w3.org/TR/webauthn-2/#sctn-privacy-considerations-client.)	2025-05-04 00:01:26.628235	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1752	\N	❌ Failed login: Unknown identifier 0781617617	2025-05-04 00:22:40.734669	192.168.60.3	python-requests/2.32.3	Unknown	t	1
1755	\N	❌ Failed login: Unknown identifier 0781617617	2025-05-04 00:36:49.972598	192.168.60.3	python-requests/2.32.3	Unknown	t	1
1760	\N	❌ Failed login: Unknown identifier 0781617617	2025-05-04 00:36:51.533254	192.168.60.3	python-requests/2.32.3	Unknown	t	1
1765	\N	❌ Failed login: Unknown identifier 0781617617	2025-05-04 00:42:16.420073	192.168.60.3	python-requests/2.32.3	Unknown	t	1
1770	\N	❌ Failed login: Unknown identifier 0781617617	2025-05-04 00:42:17.951679	192.168.60.3	python-requests/2.32.3	Unknown	t	1
1773	22	⚠️ Client-side WebAuthn failure: User cancelled or did not interact with WebAuthn prompt in time. (NotAllowedError: The operation either timed out or was not allowed. See: https://www.w3.org/TR/webauthn-2/#sctn-privacy-considerations-client.)	2025-05-04 00:48:28.362726	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1806	54	🚨 Session hijack attempt (fingerprint mismatch)	2025-05-05 04:17:06.458332	\N	\N	Unknown	f	1
1863	22	✅ Successful login	2025-05-06 12:31:25.256394	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1864	22	✅ TOTP verified successfully	2025-05-06 12:31:46.740607	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1865	22	🔐 Logged in via WebAuthn (USB security key)	2025-05-06 12:32:36.554142	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1872	54	✅ Successful login	2025-05-07 17:29:41.728928	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1873	54	✅ TOTP verified successfully	2025-05-07 17:29:59.193206	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1874	54	🔐 Logged in via WebAuthn (USB security key)	2025-05-07 17:30:25.517161	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1892	22	✅ Successful login	2025-05-08 11:32:13.432148	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1893	22	✅ TOTP verified successfully	2025-05-08 11:32:26.342188	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1894	22	🔐 Logged in via WebAuthn (USB security key)	2025-05-08 11:33:17.673462	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1598	22	✅ Successful login	2025-04-30 18:50:45.592354	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1599	22	✅ TOTP verified successfully	2025-04-30 18:51:07.628688	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1600	22	🔐 Logged in via WebAuthn (USB security key)	2025-04-30 18:51:12.241141	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1601	22	🛠️ Assigned role 'agent' to user Gabriel Darwin (SWP_1744070543)	2025-04-30 18:51:48.259072	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Headquarters	f	1
1633	54	✅ Approved withdrawal of 200.0 RWF for User 69	2025-05-02 12:36:40.681498	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Agent location	f	1
1634	22	✅ Successful login	2025-05-02 12:37:58.401055	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1711	22	⚠️ Client-side WebAuthn failure: User cancelled or did not interact with WebAuthn prompt in time. (NotAllowedError: WebAuthn is not supported on sites with TLS certificate errors.)	2025-05-03 22:58:07.101312	192.168.60.3	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1716	22	❌ Failed TOTP verification (2)	2025-05-03 22:58:44.740846	192.168.60.3	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	t	1
1719	22	⚠️ Client-side WebAuthn failure: User cancelled or did not interact with WebAuthn prompt in time. (NotAllowedError: WebAuthn is not supported on sites with TLS certificate errors.)	2025-05-03 22:59:16.329371	192.168.60.3	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1724	22	⚠️ Client-side WebAuthn failure: User cancelled or did not interact with WebAuthn prompt in time. (NotAllowedError: WebAuthn is not supported on sites with TLS certificate errors.)	2025-05-03 23:00:05.373	192.168.60.3	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1727	22	⚠️ Client-side WebAuthn failure: User cancelled or did not interact with WebAuthn prompt in time. (NotAllowedError: WebAuthn is not supported on sites with TLS certificate errors.)	2025-05-03 23:01:16.234366	192.168.60.3	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1733	22	⚠️ Client-side WebAuthn failure: User cancelled or did not interact with WebAuthn prompt in time. (NotAllowedError: The operation either timed out or was not allowed. See: https://www.w3.org/TR/webauthn-2/#sctn-privacy-considerations-client.)	2025-05-03 23:23:25.397131	192.168.60.3	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1737	54	✅ TOTP verified successfully	2025-05-03 23:37:42.657538	192.168.60.3	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1739	54	❌ Failed login: Invalid password (3)	2025-05-03 23:56:42.766977	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	t	1
1744	22	🔐 Logged in via WebAuthn (USB security key)	2025-05-04 00:02:18.048423	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1748	56	❌ Failed login: Invalid password (5)	2025-05-04 00:22:31.562193	192.168.60.3	python-requests/2.32.3	Unknown	t	1
1749	56	🚨 Account temporarily locked due to failed login attempts	2025-05-04 00:22:31.562193	192.168.60.3	python-requests/2.32.3	Unknown	t	1
1751	\N	❌ Failed login: Unknown identifier 0781617617	2025-05-04 00:22:40.42877	192.168.60.3	python-requests/2.32.3	Unknown	t	1
1759	\N	❌ Failed login: Unknown identifier 0781617617	2025-05-04 00:36:51.226007	192.168.60.3	python-requests/2.32.3	Unknown	t	1
1764	\N	❌ Failed login: Unknown identifier 0781617617	2025-05-04 00:42:16.137792	192.168.60.3	python-requests/2.32.3	Unknown	t	1
1769	\N	❌ Failed login: Unknown identifier 0781617617	2025-05-04 00:42:17.672733	192.168.60.3	python-requests/2.32.3	Unknown	t	1
1807	22	✅ Successful login	2025-05-05 14:37:55.722487	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	Unknown	f	1
1808	22	✅ TOTP verified successfully	2025-05-05 14:39:52.357916	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	Unknown	f	1
1809	22	🔐 Logged in via WebAuthn (USB security key)	2025-05-05 14:39:57.182772	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	Unknown	f	1
1810	22	🚨 Session hijack attempt (fingerprint mismatch)	2025-05-05 05:45:48.320509	\N	\N	Unknown	f	1
1812	22	📱 Admin generated SIM: 8901958464474132 with mobile 0787657484	2025-05-05 14:48:35.026059	127.0.0.1	curl/7.81.0	Headquarters	f	1
1813	22	📱 Admin generated SIM: 8901854931425236 with mobile 0787373658	2025-05-05 14:48:52.038039	192.168.2.116	curl/8.13.0	Headquarters	f	1
1866	22	✅ Successful login	2025-05-06 12:49:21.953048	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	Unknown	f	1
1867	22	✅ TOTP verified successfully	2025-05-06 12:49:41.677389	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	Unknown	f	1
1868	22	🔐 Logged in via WebAuthn (USB security key)	2025-05-06 12:49:48.013572	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	Unknown	f	1
1869	22	✅ Successful login	2025-05-06 13:07:10.053422	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	Unknown	f	1
1875	54	✅ Successful login	2025-05-07 17:52:28.585292	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Mobile Safari/537.36	Unknown	f	1
1876	54	✅ TOTP verified successfully	2025-05-07 17:52:50.850633	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Mobile Safari/537.36	Unknown	f	1
1877	54	🔐 Logged in via WebAuthn (USB security key)	2025-05-07 17:52:56.002176	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Mobile Safari/537.36	Unknown	f	1
1880	54	✅ TOTP verified successfully	2025-05-07 18:42:52.597496	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1895	22	✏️ Edited user Mamure Malakai (0782858063) — Fields updated: email	2025-05-08 11:34:43.92593	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Headquarters	f	1
1896	62	❌ Failed login: Invalid password (1)	2025-05-08 11:35:30.875608	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1602	69	❌ Failed login: Invalid password (2)	2025-04-30 19:13:59.122479	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1604	69	✅ TOTP verified successfully	2025-04-30 19:15:07.605948	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1605	69	🔐 Logged in via WebAuthn (USB security key)	2025-04-30 19:19:58.680937	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1637	22	📱 Admin generated SIM: 8901270367573968 with mobile 0787880352	2025-05-02 12:44:29.387598	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Headquarters	f	1
1638	22	💸 Funded agent Pathos (0787832379) with 30000.0 RWF from HQ Wallet	2025-05-02 12:45:24.753756	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	{"lat": 34.7314883, "lng": 135.7347076}	f	1
1641	22	🚫 Suspended user Alice Niyonsenga (N/A) and marked for deletion.	2025-05-02 12:50:04.25525	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Headquarters	t	1
1642	22	🗑️ Deleted user Alice Niyonsenga (N/A) and all associated records	2025-05-02 12:50:19.874748	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Headquarters	t	1
1713	22	⚠️ Client-side WebAuthn failure: User cancelled or did not interact with WebAuthn prompt in time. (NotAllowedError: WebAuthn is not supported on sites with TLS certificate errors.)	2025-05-03 22:58:21.32736	192.168.60.3	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1715	22	⚠️ Client-side WebAuthn failure: User cancelled or did not interact with WebAuthn prompt in time. (NotAllowedError: WebAuthn is not supported on sites with TLS certificate errors.)	2025-05-03 22:58:42.420302	192.168.60.3	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1721	22	⚠️ Client-side WebAuthn failure: User cancelled or did not interact with WebAuthn prompt in time. (NotAllowedError: WebAuthn is not supported on sites with TLS certificate errors.)	2025-05-03 22:59:58.904236	192.168.60.3	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1736	54	✅ Successful login	2025-05-03 23:36:24.885002	192.168.60.3	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1738	54	🔐 Logged in via WebAuthn (USB security key)	2025-05-03 23:37:48.952415	192.168.60.3	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1747	56	❌ Failed login: Invalid password (4)	2025-05-04 00:22:31.210694	192.168.60.3	python-requests/2.32.3	Unknown	t	1
1750	\N	❌ Failed login: Unknown identifier 0781617617	2025-05-04 00:22:40.190476	192.168.60.3	python-requests/2.32.3	Unknown	t	1
1758	\N	❌ Failed login: Unknown identifier 0781617617	2025-05-04 00:36:50.91946	192.168.60.3	python-requests/2.32.3	Unknown	t	1
1768	\N	❌ Failed login: Unknown identifier 0781617617	2025-05-04 00:42:17.3662	192.168.60.3	python-requests/2.32.3	Unknown	t	1
1811	22	🚨 Session hijack attempt (fingerprint mismatch)	2025-05-05 05:46:14.073307	\N	\N	Unknown	f	1
1870	22	✅ TOTP verified successfully	2025-05-06 13:08:14.483257	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	Unknown	f	1
1871	22	🔐 Logged in via WebAuthn (USB security key)	2025-05-06 13:08:19.532466	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	Unknown	f	1
1878	54	🔄 SIM swapped for 0784690255: 8901765884990587 ➡️ 8901119623841129	2025-05-07 17:53:50.364464	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Mobile Safari/537.36	Unknown	t	1
1897	62	❌ Failed login: Invalid password (2)	2025-05-08 11:35:37.736079	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1899	62	✅ Successful login	2025-05-08 11:35:52.070212	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1900	54	✅ Successful login	2025-05-08 11:36:37.126768	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1603	69	✅ Successful login	2025-04-30 19:14:05.154424	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1639	22	🚫 Suspended user Kamanzi Niyonsaba (N/A) and marked for deletion.	2025-05-02 12:49:29.897253	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Headquarters	t	1
1640	22	🗑️ Deleted user Kamanzi Niyonsaba (N/A) and all associated records	2025-05-02 12:49:41.104246	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Headquarters	t	1
1814	22	🚨 Session hijack attempt (fingerprint mismatch)	2025-05-05 05:51:05.433874	\N	\N	Unknown	f	1
1815	22	🚨 Session hijack attempt (fingerprint mismatch)	2025-05-05 05:51:13.370887	\N	\N	Unknown	f	1
1879	54	✅ Successful login	2025-05-07 18:42:39.892721	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1881	54	🔐 Logged in via WebAuthn (USB security key)	2025-05-07 18:42:57.283053	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1898	62	❌ Failed login: Invalid password (3)	2025-05-08 11:35:45.69417	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	t	1
1901	54	✅ TOTP verified successfully	2025-05-08 11:36:47.832364	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1902	54	🔐 Logged in via WebAuthn (USB security key)	2025-05-08 11:36:52.715361	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
379	22	✅ Successful login	2025-04-12 11:14:48.379431	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
1643	54	📧 Password reset requested	2025-05-02 13:04:17.827943	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1644	54	❌ Attempted to reuse an old password during reset	2025-05-02 13:05:13.196066	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	t	1
1645	54	❌ Attempted to reuse an old password during reset	2025-05-02 13:05:53.2141	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	t	1
1646	54	❌ Attempted to reuse an old password during reset	2025-05-02 13:06:57.702353	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	t	1
1647	56	📧 Password reset requested	2025-05-02 13:09:23.604513	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1648	56	📧 Password reset requested	2025-05-02 13:27:46.457642	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1649	56	✅ Password reset after MFA and checks	2025-05-02 13:28:35.28265	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1650	56	✅ Successful login	2025-05-02 13:30:44.014828	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1651	56	✅ TOTP verified successfully	2025-05-02 13:31:39.525074	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1652	56	🔐 Logged in via WebAuthn (USB security key)	2025-05-02 13:31:45.574478	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1654	69	❌ Failed login: Invalid password (1)	2025-05-02 13:42:30.825895	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1658	22	🔁 Reversal initiated: TX #211 — 100.0 RWF back to sender	2025-05-02 13:47:16.098872	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Headquarters	t	1
1816	61	❌ Failed login: Invalid password (1)	2025-05-05 15:20:31.401665	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1817	61	❌ Failed login: Invalid password (2)	2025-05-05 15:20:39.671554	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1818	22	✅ Successful login	2025-05-05 15:20:53.201085	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	Unknown	f	1
1819	22	✅ TOTP verified successfully	2025-05-05 15:21:09.437846	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	Unknown	f	1
1820	22	🔐 Logged in via WebAuthn (USB security key)	2025-05-05 15:21:16.205926	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	Unknown	f	1
1821	55	❌ Failed login: Invalid password (1)	2025-05-05 15:21:50.283459	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1823	55	❌ Failed login: Invalid password (3)	2025-05-05 15:22:02.260101	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	t	1
1825	55	✅ Successful login	2025-05-05 15:22:23.496791	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1827	55	❌ Failed TOTP verification (2)	2025-05-05 15:22:52.541905	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	t	1
1830	55	🚨 Session hijack attempt (fingerprint mismatch)	2025-05-05 06:24:14.56033	\N	\N	Unknown	f	1
1832	55	🚨 Session hijack attempt (fingerprint mismatch)	2025-05-05 06:25:40.075686	\N	\N	Unknown	f	1
1834	55	✅ Successful login	2025-05-05 15:26:22.673797	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	Unknown	f	1
1837	55	🚨 Session hijack attempt (fingerprint mismatch)	2025-05-05 06:30:52.702164	\N	\N	Unknown	f	1
1838	55	🚨 Session hijack attempt (fingerprint mismatch)	2025-05-05 06:32:51.325472	\N	\N	Unknown	f	1
1839	55	🚨 Session hijack attempt (fingerprint mismatch)	2025-05-05 06:34:19.449645	\N	\N	Unknown	f	1
1841	55	✅ Successful login	2025-05-05 16:22:23.503761	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	Unknown	f	1
1844	55	Withdrawal of 1000.0 RWF	2025-05-05 16:25:55.937157	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0		f	1
1882	54	🔄 SIM swapped for 0787167297: 8901257170530088 ➡️ 8901612403911700	2025-05-07 18:49:20.782554	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	t	1
1903	54	❌ Failed login: Invalid password (1)	2025-05-08 12:04:08.517915	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1904	54	❌ Failed login: Invalid password (2)	2025-05-08 12:04:15.002132	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1905	54	❌ Failed login: Invalid password (3)	2025-05-08 12:04:20.938852	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	t	1
1906	54	✅ Successful login	2025-05-08 12:04:41.93152	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1907	54	✅ TOTP verified successfully	2025-05-08 12:04:55.29794	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1908	54	🔐 Logged in via WebAuthn (USB security key)	2025-05-08 12:05:01.296734	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1921	54	✅ Successful login	2025-05-11 10:23:48.375692	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1922	54	✅ TOTP verified successfully	2025-05-11 10:24:08.094877	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1923	54	🔐 Logged in via WebAuthn (USB security key)	2025-05-11 10:24:37.176148	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1997	56	✅ Successful login	2025-05-12 09:38:22.313086	127.0.0.1	IAMaaS API Access	Unknown	f	2
2036	\N	❌ Failed login: Unknown identifier ' OR 1=1 --	2025-05-12 15:22:09.729602	192.168.2.116	curl/8.13.0	Unknown	t	1
2037	\N	❌ Failed login: Unknown identifier ' OR 1=1 --	2025-05-12 15:22:53.59314	192.168.2.116	curl/8.13.0	Unknown	t	1
1653	56	🧾 Agent deposited 500.0 RWF to bztn (0784690255)	2025-05-02 13:40:54.694523	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	34.7315, 135.7347	f	1
1655	22	✅ Successful login	2025-05-02 13:43:28.561862	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1657	22	🔐 Logged in via WebAuthn (USB security key)	2025-05-02 13:43:58.329551	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1822	55	❌ Failed login: Invalid password (2)	2025-05-05 15:21:56.742754	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1824	55	❌ Failed login: Invalid password (4)	2025-05-05 15:22:08.015737	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	t	1
1826	55	❌ Failed TOTP verification (1)	2025-05-05 15:22:39.343936	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	t	1
1828	55	✅ TOTP verified successfully	2025-05-05 15:23:15.605844	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1829	55	🔐 Logged in via WebAuthn (USB security key)	2025-05-05 15:23:22.733535	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1831	55	🚨 Session hijack attempt (fingerprint mismatch)	2025-05-05 06:25:38.793171	\N	\N	Unknown	f	1
1833	55	❌ Failed TOTP verification (3)	2025-05-05 15:25:52.361088	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Mobile Safari/537.36	Unknown	t	1
1835	55	✅ TOTP verified successfully	2025-05-05 15:26:44.498571	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	Unknown	f	1
1836	55	🔐 Logged in via WebAuthn (USB security key)	2025-05-05 15:26:49.876933	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	Unknown	f	1
1840	55	🚨 Session hijack attempt (fingerprint mismatch)	2025-05-05 06:34:25.072467	\N	\N	Unknown	f	1
1842	55	✅ TOTP verified successfully	2025-05-05 16:22:40.989656	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	Unknown	f	1
1843	55	🔐 Logged in via WebAuthn (USB security key)	2025-05-05 16:22:47.673653	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	Unknown	f	1
1883	54	✅ TOTP verified successfully	2025-05-07 18:56:20.708774	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Mobile Safari/537.36	Unknown	f	1
1884	54	⚠️ Client-side WebAuthn failure: Unknown client-side WebAuthn error. (SyntaxError: Unexpected token '<', "<!doctype "... is not valid JSON)	2025-05-07 18:56:21.916462	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Mobile Safari/537.36	Unknown	f	1
1909	54	✅ Successful login	2025-05-08 13:03:41.279056	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1910	54	✅ TOTP verified successfully	2025-05-08 13:03:51.646911	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1911	54	🔐 Logged in via WebAuthn (USB security key)	2025-05-08 13:03:56.22657	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1924	54	✅ Successful login	2025-05-11 10:41:17.29897	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1925	54	✅ TOTP verified successfully	2025-05-11 10:41:27.911256	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1926	54	🔐 Logged in via WebAuthn (USB security key)	2025-05-11 10:41:32.766663	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1998	54	✅ Successful login	2025-05-12 09:39:45.885369	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1999	54	✅ TOTP verified successfully	2025-05-12 09:40:12.934479	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
2000	54	🔐 Logged in via WebAuthn (USB security key)	2025-05-12 09:40:49.718791	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
2038	\N	❌ Failed login: Unknown identifier ' OR 1=1 --	2025-05-12 15:30:23.145212	192.168.2.116	curl/8.13.0	Unknown	t	1
2039	\N	❌ Failed login: Unknown identifier ' OR 'a'='a	2025-05-12 15:31:33.870977	192.168.2.116	curl/8.13.0	Unknown	t	1
2040	\N	❌ Failed login: Unknown identifier test	2025-05-12 15:51:45.827404	192.168.2.116	sqlmap/1.9.4#stable (https://sqlmap.org)	Unknown	t	1
2041	\N	❌ Failed login: Unknown identifier test	2025-05-12 15:54:08.534519	192.168.2.116	sqlmap/1.9.4#stable (https://sqlmap.org)	Unknown	t	1
1656	22	✅ TOTP verified successfully	2025-05-02 13:43:52.302085	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1845	\N	❌ Failed login: Unknown identifier ' OR 1=1 --	2025-05-05 17:30:15.062464	192.168.2.116	curl/8.13.0	Unknown	t	1
1846	55	✅ Successful login	2025-05-05 17:51:40.798198	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	Unknown	f	1
1885	54	✅ Successful login	2025-05-07 18:58:23.640242	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Mobile Safari/537.36	Unknown	f	1
1886	54	✅ TOTP verified successfully	2025-05-07 18:58:38.184255	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Mobile Safari/537.36	Unknown	f	1
1887	54	🔐 Logged in via WebAuthn (USB security key)	2025-05-07 18:58:43.482161	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Mobile Safari/537.36	Unknown	f	1
1912	54	✅ Successful login	2025-05-08 13:30:53.38977	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1913	54	✅ TOTP verified successfully	2025-05-08 13:31:11.565321	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1914	54	🔐 Logged in via WebAuthn (USB security key)	2025-05-08 13:31:16.429148	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1927	54	✅ Successful login	2025-05-11 10:58:26.922583	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1928	54	✅ TOTP verified successfully	2025-05-11 10:58:42.395806	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1929	54	🔐 Logged in via WebAuthn (USB security key)	2025-05-11 10:58:47.347225	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1930	62	❌ SIM swap verification failed (bad password)	2025-05-11 10:59:34.085807	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	t	1
2001	56	❌ Failed login: Invalid password (1)	2025-05-12 09:52:56.394605	192.168.2.116	python-requests/2.32.3	Unknown	f	1
2002	56	❌ Failed login: Invalid password (2)	2025-05-12 09:52:56.750481	192.168.2.116	python-requests/2.32.3	Unknown	f	1
2003	56	❌ Failed login: Invalid password (3)	2025-05-12 09:52:57.119282	192.168.2.116	python-requests/2.32.3	Unknown	t	1
2004	56	❌ Failed login: Invalid password (4)	2025-05-12 09:52:57.495181	192.168.2.116	python-requests/2.32.3	Unknown	t	1
2005	56	❌ Failed login: Invalid password (5)	2025-05-12 09:52:57.871345	192.168.2.116	python-requests/2.32.3	Unknown	t	1
2006	56	🚨 Account temporarily locked due to failed login attempts	2025-05-12 09:52:57.871345	192.168.2.116	python-requests/2.32.3	Unknown	t	1
2007	\N	❌ Failed login: Unknown identifier 0781617617	2025-05-12 09:53:04.715845	192.168.2.116	python-requests/2.32.3	Unknown	t	1
2008	\N	❌ Failed login: Unknown identifier 0781617617	2025-05-12 09:53:05.0306	192.168.2.116	python-requests/2.32.3	Unknown	t	1
2009	\N	❌ Failed login: Unknown identifier 0781617617	2025-05-12 09:53:05.350212	192.168.2.116	python-requests/2.32.3	Unknown	t	1
2010	\N	❌ Failed login: Unknown identifier 0781617617	2025-05-12 09:53:05.665715	192.168.2.116	python-requests/2.32.3	Unknown	t	1
2011	\N	❌ Failed login: Unknown identifier 0781617617	2025-05-12 09:53:05.996904	192.168.2.116	python-requests/2.32.3	Unknown	t	1
2012	\N	❌ Failed login: Unknown identifier 0781617617	2025-05-12 09:53:06.27059	192.168.2.116	python-requests/2.32.3	Unknown	t	1
2013	\N	❌ Failed login: Unknown identifier 0781617617	2025-05-12 09:53:06.592695	192.168.2.116	python-requests/2.32.3	Unknown	t	1
2014	22	✅ Successful login	2025-05-12 09:56:15.64605	192.168.2.116	Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0	Unknown	f	1
2015	22	❌ Failed TOTP verification (1)	2025-05-12 09:56:32.866571	192.168.2.116	Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0	Unknown	t	1
2016	22	✅ TOTP verified successfully	2025-05-12 09:56:43.561536	192.168.2.116	Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0	Unknown	f	1
2017	22	⚠️ Client-side WebAuthn failure: User cancelled or did not interact with WebAuthn prompt in time. (NotAllowedError: The request is not allowed by the user agent or the platform in the current context, possibly because the user denied permission.)	2025-05-12 09:56:59.802684	192.168.2.116	Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0	Unknown	f	1
2018	22	⚠️ Client-side WebAuthn failure: User cancelled or did not interact with WebAuthn prompt in time. (NotAllowedError: The request is not allowed by the user agent or the platform in the current context, possibly because the user denied permission.)	2025-05-12 09:57:18.572197	192.168.2.116	Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0	Unknown	f	1
2019	22	✅ Successful login	2025-05-12 09:58:57.747766	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
2020	22	✅ TOTP verified successfully	2025-05-12 09:59:12.380054	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
2021	22	🔐 Logged in via WebAuthn (USB security key)	2025-05-12 09:59:17.542856	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
2022	54	❌ Failed login: User not under tenant	2025-05-12 10:00:20.107313	127.0.0.1	IAMaaS API Access	Unknown	t	2
2042	\N	❌ Failed login: Unknown identifier test	2025-05-12 16:14:24.455986	192.168.2.116	curl/8.13.0	Unknown	t	1
2043	54	✅ Successful login	2025-05-12 16:31:55.220812	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
2044	54	✅ TOTP verified successfully	2025-05-12 16:32:12.707231	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
2045	54	🔐 Logged in via WebAuthn (USB security key)	2025-05-12 16:32:39.515082	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
2048	54	✅ TOTP verified successfully	2025-05-12 16:34:49.882429	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	Unknown	f	1
2085	54	✅ Successful login	2025-05-13 10:37:42.715478	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
2086	54	❌ Failed TOTP verification (1)	2025-05-13 10:38:08.668283	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	t	1
1659	69	✅ Reversal completed: 100.0 RWF refunded to sender for TX #211	2025-05-02 13:47:26.128648	System	Auto Processor	Headquarters	f	1
1847	55	✅ TOTP verified successfully	2025-05-05 17:53:42.300001	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	Unknown	f	1
1848	55	🔐 Logged in via WebAuthn (USB security key)	2025-05-05 17:53:48.420245	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	Unknown	f	1
1849	22	✅ Successful login	2025-05-05 18:22:56.782503	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	Unknown	f	1
1853	22	✅ TOTP verified successfully	2025-05-05 18:39:07.655545	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	Unknown	f	1
1854	22	🔐 Logged in via WebAuthn (USB security key)	2025-05-05 18:39:12.782355	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	Unknown	f	1
1857	22	✅ Successful login	2025-05-05 19:13:35.213527	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	Unknown	f	1
1861	22	🚨 Session hijack attempt (fingerprint mismatch)	2025-05-05 10:17:28.577214	\N	\N	Unknown	f	1
1888	22	✅ Successful login	2025-05-07 19:14:29.09097	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Mobile Safari/537.36	Unknown	f	1
1890	22	🔐 Logged in via WebAuthn (USB security key)	2025-05-07 19:14:49.988775	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Mobile Safari/537.36	Unknown	f	1
1891	22	📱 Admin generated SIM: 8901639177604566 with mobile 0787611277	2025-05-07 19:16:15.694328	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Mobile Safari/537.36	Headquarters	f	1
1915	54	✅ Successful login	2025-05-08 13:49:59.337179	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1916	54	✅ TOTP verified successfully	2025-05-08 13:50:13.908123	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1917	54	🔐 Logged in via WebAuthn (USB security key)	2025-05-08 13:50:18.789271	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1931	62	❌ SIM swap verification failed (bad TOTP)	2025-05-11 10:59:46.145144	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	t	1
2023	57	✅ Successful login	2025-05-12 10:00:41.771143	127.0.0.1	IAMaaS API Access	Unknown	f	2
2024	57	🚨 Session hijack attempt on agent account (fingerprint mismatch)	2025-05-12 01:05:05.475298	127.0.0.1	curl/7.81.0	Unknown	t	1
2046	54	🚨 Session hijack attempt on agent account (fingerprint mismatch)	2025-05-12 07:32:56.301642	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Mobile Safari/537.36	Unknown	t	1
2087	54	✅ TOTP verified successfully	2025-05-13 10:38:26.972874	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
2088	54	⚠️ Client-side WebAuthn failure: User cancelled or did not interact with WebAuthn prompt in time. (NotAllowedError: The operation either timed out or was not allowed. See: https://www.w3.org/TR/webauthn-2/#sctn-privacy-considerations-client.)	2025-05-13 10:38:52.396188	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
2089	54	🔐 Logged in via WebAuthn (USB security key)	2025-05-13 10:39:02.172837	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1660	22	🛠️ Assigned role 'agent' to user bztn Lab (0784690255)	2025-05-02 13:50:21.840505	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Headquarters	f	1
1662	22	👁️ Viewed profile of bztn Lab (0784690255)	2025-05-02 13:50:46.619871	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Headquarters	f	1
1850	22	✅ TOTP verified successfully	2025-05-05 18:23:15.323117	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	Unknown	f	1
1851	22	🔐 Logged in via WebAuthn (USB security key)	2025-05-05 18:23:20.495671	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	Unknown	f	1
1852	22	✅ Successful login	2025-05-05 18:38:49.038893	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	Unknown	f	1
1855	22	🚨 Session hijack attempt (fingerprint mismatch)	2025-05-05 09:41:40.082932	\N	\N	Unknown	f	1
1856	22	🚨 Session hijack attempt (fingerprint mismatch)	2025-05-05 09:45:10.174921	\N	\N	Unknown	f	1
1858	22	✅ TOTP verified successfully	2025-05-05 19:13:48.440427	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	Unknown	f	1
1859	22	🔐 Logged in via WebAuthn (USB security key)	2025-05-05 19:13:53.763074	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	Unknown	f	1
1860	22	🚨 Session hijack attempt (fingerprint mismatch)	2025-05-05 10:16:45.268643	\N	\N	Unknown	f	1
1862	69	❌ Failed login: Invalid password (1)	2025-05-05 20:11:05.462354	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1889	22	✅ TOTP verified successfully	2025-05-07 19:14:45.444255	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Mobile Safari/537.36	Unknown	f	1
1918	62	✅ Successful login	2025-05-08 13:57:18.80771	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1919	62	✅ TOTP verified successfully	2025-05-08 13:57:47.414793	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1920	62	🔐 Logged in via WebAuthn (USB security key)	2025-05-08 13:57:54.894715	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1932	54	✅ Successful login	2025-05-11 11:15:41.180607	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1933	54	✅ TOTP verified successfully	2025-05-11 11:15:51.418176	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1934	54	🔐 Logged in via WebAuthn (USB security key)	2025-05-11 11:15:56.487048	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
2025	55	✅ Successful login	2025-05-12 10:43:56.749497	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	Unknown	f	1
2026	55	✅ TOTP verified successfully	2025-05-12 10:44:12.597628	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	Unknown	f	1
2027	55	🔐 Logged in via WebAuthn (USB security key)	2025-05-12 10:44:19.064307	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	Unknown	f	1
2030	57	✅ Successful login	2025-05-12 10:57:59.123316	127.0.0.1	IAMaaS API Access	Unknown	f	2
2031	54	✅ Successful login	2025-05-12 11:05:29.122436	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	Unknown	f	1
2047	54	✅ Successful login	2025-05-12 16:34:39.717144	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	Unknown	f	1
2049	54	🔐 Logged in via WebAuthn (USB security key)	2025-05-12 16:34:55.167489	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	Unknown	f	1
2090	54	✅ Successful login	2025-05-13 15:27:52.849447	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
2091	54	✅ TOTP verified successfully	2025-05-13 15:28:44.671267	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
2092	54	🔐 Logged in via WebAuthn (USB security key)	2025-05-13 15:29:06.317054	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
2093	22	✅ Successful login	2025-05-13 17:11:39.858331	192.168.2.116	Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0	Unknown	f	1
2094	22	❌ Failed TOTP verification (1)	2025-05-13 17:11:59.988406	192.168.2.116	Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0	Unknown	t	1
2095	22	✅ TOTP verified successfully	2025-05-13 17:12:11.008457	192.168.2.116	Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0	Unknown	f	1
1661	22	✅ Verified and reactivated user bztn Lab (0784690255)	2025-05-02 13:50:38.087101	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Headquarters	f	1
1935	62	❌ SIM swap verification failed (bad TOTP)	2025-05-11 11:23:34.867073	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	t	1
2028	57	✅ Successful login	2025-05-12 10:57:07.584538	127.0.0.1	IAMaaS API Access	Unknown	f	2
2029	\N	❌ Failed login: Unknown identifier 0787408912	2025-05-12 10:57:51.195876	127.0.0.1	IAMaaS API Access	Unknown	t	2
2032	54	✅ TOTP verified successfully	2025-05-12 11:05:44.221057	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	Unknown	f	1
2033	54	🔐 Logged in via WebAuthn (USB security key)	2025-05-12 11:05:48.840216	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	Unknown	f	1
2050	54	🚨 Session hijack attempt on agent account (fingerprint mismatch)	2025-05-12 07:43:55.502224	192.168.2.116	curl/8.13.0	Unknown	t	1
2051	54	🚨 Session hijack attempt on agent account (fingerprint mismatch)	2025-05-12 07:49:00.643814	192.168.2.116	curl/8.13.0	Unknown	t	1
1663	22	🚫 Suspended user bztn Lab (0784690255) and marked for deletion.	2025-05-02 13:51:04.206663	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Headquarters	t	1
1936	62	❌ SIM swap verification failed (bad TOTP)	2025-05-11 11:25:04.046843	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	t	1
2034	54	🚨 Session hijack attempt on agent account (fingerprint mismatch)	2025-05-12 02:07:15.518972	127.0.0.1	curl/7.81.0	Unknown	t	1
2053	54	✅ Successful login	2025-05-12 17:03:51.202612	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	Unknown	f	1
2054	54	✅ TOTP verified successfully	2025-05-12 17:04:13.658154	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	Unknown	f	1
2055	54	🔐 Logged in via WebAuthn (USB security key)	2025-05-12 17:04:18.197647	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	Unknown	f	1
2056	54	✅ Successful login	2025-05-12 17:11:20.581674	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
2058	54	🔐 Logged in via WebAuthn (USB security key)	2025-05-12 17:11:46.159982	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
2060	70	✅ Successful login	2025-05-12 17:16:54.056223	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	Unknown	f	1
2062	70	✅ Successful login	2025-05-12 17:18:38.655479	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
2066	54	✅ TOTP verified successfully	2025-05-12 17:23:09.279079	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
2071	70	❌ Failed login: User not under tenant	2025-05-12 17:39:02.309406	127.0.0.1	IAMaaS API Access	Unknown	t	2
2076	22	✅ TOTP verified successfully	2025-05-12 17:49:42.568382	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
2079	55	✅ TOTP verified successfully	2025-05-12 19:19:07.043579	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	Unknown	f	1
1664	22	✅ Verified and reactivated user Mamure Malakai (0782858063)	2025-05-02 13:51:53.097169	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Headquarters	f	1
1937	54	✅ Successful login	2025-05-11 11:39:35.238699	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1938	54	✅ TOTP verified successfully	2025-05-11 11:39:47.058915	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1939	54	🔐 Logged in via WebAuthn (USB security key)	2025-05-11 11:39:52.174121	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
2035	54	🚨 Session hijack attempt on agent account (fingerprint mismatch)	2025-05-12 02:07:53.019372	192.168.2.116	curl/8.13.0	Unknown	t	1
2057	54	✅ TOTP verified successfully	2025-05-12 17:11:37.872357	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
2065	54	✅ Successful login	2025-05-12 17:22:52.532534	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
2067	54	🔐 Logged in via WebAuthn (USB security key)	2025-05-12 17:23:14.640451	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
2075	22	✅ Successful login	2025-05-12 17:48:40.255319	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
2077	22	🔐 Logged in via WebAuthn (USB security key)	2025-05-12 17:49:47.761251	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
2078	55	✅ Successful login	2025-05-12 19:18:36.464306	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	Unknown	f	1
2080	55	🔐 Logged in via WebAuthn (USB security key)	2025-05-12 19:19:11.427259	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	Unknown	f	1
1665	22	📱 Admin generated SIM: 8901881337582643 with mobile 0787622098	2025-05-02 13:52:24.830746	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Headquarters	f	1
2059	70	🆕 New user registered using ICCID 8901839465275236 (SIM created by: 54)	2025-05-12 17:16:27.988791	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	Unknown	f	1
2061	70	✅ TOTP verified successfully	2025-05-12 17:17:35.713534	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	Unknown	f	1
2072	\N	❌ Failed login: Unknown identifier 0789996960	2025-05-12 17:39:11.725055	127.0.0.1	IAMaaS API Access	Unknown	t	2
2083	55	🚨 Session hijack attempt on user account (fingerprint mismatch)	2025-05-12 10:25:08.949101	127.0.0.1	curl/7.81.0	Unknown	t	1
1941	62	❌ SIM swap verification failed (bad TOTP)	2025-05-11 11:47:27.950671	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	t	1
2063	70	✅ TOTP verified successfully	2025-05-12 17:18:55.281616	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
2069	56	✅ Password reset after MFA and checks	2025-05-12 17:31:03.447171	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
2073	\N	❌ Failed login: Unknown identifier 078999696	2025-05-12 17:39:18.683831	127.0.0.1	IAMaaS API Access	Unknown	t	2
2082	55	🚨 Session hijack attempt on user account (fingerprint mismatch)	2025-05-12 10:20:00.631158	192.168.2.116	curl/8.13.0	Unknown	t	1
2064	70	🔐 Logged in via WebAuthn (USB security key)	2025-05-12 17:19:41.032789	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
2068	56	📧 Password reset requested	2025-05-12 17:29:52.451568	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	Unknown	f	1
2070	57	✅ Successful login	2025-05-12 17:38:01.153227	127.0.0.1	IAMaaS API Access	Unknown	f	2
2074	70	❌ Failed login: User not under tenant	2025-05-12 17:39:27.438399	127.0.0.1	IAMaaS API Access	Unknown	t	2
2081	55	🚨 Session hijack attempt on user account (fingerprint mismatch)	2025-05-12 10:19:52.485528	127.0.0.1	curl/7.81.0	Unknown	t	1
2084	55	🚨 Session hijack attempt on user account (fingerprint mismatch)	2025-05-12 10:25:25.804441	192.168.2.116	curl/8.13.0	Unknown	t	1
1944	54	✅ Successful login	2025-05-11 11:56:54.788854	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1945	54	✅ TOTP verified successfully	2025-05-11 11:57:08.51554	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1946	54	🔐 Logged in via WebAuthn (USB security key)	2025-05-11 11:57:14.837275	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1948	62	❌ SIM swap verification failed (bad TOTP)	2025-05-11 12:03:39.488727	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	t	1
1949	62	❌ SIM swap verification failed (bad TOTP)	2025-05-11 12:04:04.058995	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	t	1
1950	62	❌ SIM swap verification failed (bad TOTP)	2025-05-11 12:05:13.289682	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	t	1
1951	62	❌ SIM swap verification failed (bad TOTP)	2025-05-11 12:06:00.745327	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	t	1
1952	62	❌ SIM swap verification failed (bad TOTP)	2025-05-11 12:08:19.956136	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	t	1
1953	62	❌ SIM swap verification failed (bad TOTP)	2025-05-11 12:08:23.799986	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	t	1
1954	54	✅ Successful login	2025-05-11 12:13:06.996238	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1955	54	✅ TOTP verified successfully	2025-05-11 12:13:17.218252	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1956	54	🔐 Logged in via WebAuthn (USB security key)	2025-05-11 12:13:21.410161	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1959	62	❌ SIM swap verification failed (bad TOTP)	2025-05-11 12:28:28.648583	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	t	1
1960	54	❌ Failed login: Invalid password (1)	2025-05-11 12:29:19.170704	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1961	54	✅ Successful login	2025-05-11 12:29:26.328357	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1962	54	✅ TOTP verified successfully	2025-05-11 12:29:36.917486	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1963	54	🔐 Logged in via WebAuthn (USB security key)	2025-05-11 12:29:41.396507	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
2	55	❌ Failed login: Invalid password	2025-04-07 12:02:51.824409	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
1965	62	❌ SIM swap verification failed (bad TOTP)	2025-05-11 12:34:55.098695	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	t	1
1966	54	✅ Successful login	2025-05-11 12:51:12.478009	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1967	54	✅ TOTP verified successfully	2025-05-11 12:51:24.338612	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1968	54	🔐 Logged in via WebAuthn (USB security key)	2025-05-11 12:51:28.275895	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1970	62	📧 Password reset requested	2025-05-11 15:02:37.733568	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1972	22	✅ Successful login	2025-05-11 15:04:28.30391	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1974	22	🔐 Logged in via WebAuthn (USB security key)	2025-05-11 15:04:53.911601	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1976	22	✅ TOTP verified successfully	2025-05-11 15:33:06.508449	192.168.60.3	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1978	22	✅ Successful login	2025-05-11 16:10:24.487453	192.168.60.3	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1980	22	🔐 Logged in via WebAuthn (cross-device passkey)	2025-05-11 16:10:42.547175	192.168.60.3	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1984	56	❌ Failed login: Invalid password (4)	2025-05-11 16:16:22.435711	192.168.60.3	python-requests/2.32.3	Unknown	t	1
1988	\N	❌ Failed login: Unknown identifier 0781617617	2025-05-11 16:16:29.725961	192.168.60.3	python-requests/2.32.3	Unknown	t	1
1993	\N	❌ Failed login: Unknown identifier 0781617617	2025-05-11 16:16:31.544891	192.168.60.3	python-requests/2.32.3	Unknown	t	1
1969	62	✅ Verified SIM Swap 8901871711562650 ➡️ 8901669232128606	2025-05-11 12:52:17.50155	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1973	22	✅ TOTP verified successfully	2025-05-11 15:04:48.362333	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1979	22	✅ TOTP verified successfully	2025-05-11 16:10:38.8721	192.168.60.3	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1985	56	❌ Failed login: Invalid password (5)	2025-05-11 16:16:22.850821	192.168.60.3	python-requests/2.32.3	Unknown	t	1
1986	56	🚨 Account temporarily locked due to failed login attempts	2025-05-11 16:16:22.850821	192.168.60.3	python-requests/2.32.3	Unknown	t	1
1989	\N	❌ Failed login: Unknown identifier 0781617617	2025-05-11 16:16:30.137919	192.168.60.3	python-requests/2.32.3	Unknown	t	1
1994	22	✅ Successful login	2025-05-11 16:21:01.922706	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1996	22	🔐 Logged in via WebAuthn (USB security key)	2025-05-11 16:21:31.420227	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1971	62	✅ Password reset after MFA and checks	2025-05-11 15:03:42.164559	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1982	56	❌ Failed login: Invalid password (2)	2025-05-11 16:16:21.633668	192.168.60.3	python-requests/2.32.3	Unknown	f	1
1991	\N	❌ Failed login: Unknown identifier 0781617617	2025-05-11 16:16:30.916211	192.168.60.3	python-requests/2.32.3	Unknown	t	1
3	55	❌ Failed login: Invalid password	2025-04-07 12:03:05.193569	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
1975	22	✅ Successful login	2025-05-11 15:32:44.803371	192.168.60.3	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1977	22	🔐 Logged in via WebAuthn (cross-device passkey)	2025-05-11 15:33:29.591033	192.168.60.3	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
1983	56	❌ Failed login: Invalid password (3)	2025-05-11 16:16:22.025014	192.168.60.3	python-requests/2.32.3	Unknown	t	1
1987	\N	❌ Failed login: Unknown identifier 0781617617	2025-05-11 16:16:29.394785	192.168.60.3	python-requests/2.32.3	Unknown	t	1
1992	\N	❌ Failed login: Unknown identifier 0781617617	2025-05-11 16:16:31.199179	192.168.60.3	python-requests/2.32.3	Unknown	t	1
1981	56	❌ Failed login: Invalid password (1)	2025-05-11 16:16:21.22068	192.168.60.3	python-requests/2.32.3	Unknown	f	1
1990	\N	❌ Failed login: Unknown identifier 0781617617	2025-05-11 16:16:30.547655	192.168.60.3	python-requests/2.32.3	Unknown	t	1
1995	22	✅ TOTP verified successfully	2025-05-11 16:21:24.890748	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	Unknown	f	1
4	55	✅ Successful login	2025-04-07 12:03:10.12257	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
5	22	✅ Successful login	2025-04-07 12:04:14.210393	192.168.2.110	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
6	55	❌ Failed login: Invalid password (2 recent failures)	2025-04-07 12:13:39.533614	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
7	55	❌ Failed login: Invalid password (3 recent failures)	2025-04-07 12:13:43.790081	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
8	55	🚨 Brute force warning: Multiple failed login attempts	2025-04-07 12:13:43.790081	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
9	55	❌ Failed login: Invalid password (5 recent failures)	2025-04-07 12:13:47.963263	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
10	55	🚨 Brute force warning: Multiple failed login attempts	2025-04-07 12:13:47.963263	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
11	55	❌ Failed login: Invalid password (7 recent failures)	2025-04-07 12:13:51.607015	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
12	55	🚨 Brute force warning: Multiple failed login attempts	2025-04-07 12:13:51.607015	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
13	55	✅ Successful login	2025-04-07 12:13:56.915126	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
14	22	✅ Successful login	2025-04-07 14:47:11.5854	192.168.2.110	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
15	22	❌ Failed login: Invalid password (0 recent failures)	2025-04-07 14:47:56.326099	192.168.2.110	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
16	22	❌ Failed login: Invalid password (1 recent failures)	2025-04-07 14:48:02.432972	192.168.2.110	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
17	22	❌ Failed login: Invalid password (2 recent failures)	2025-04-07 14:48:05.541193	192.168.2.110	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
18	22	✅ Successful login	2025-04-07 14:48:13.720535	192.168.2.110	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
19	55	✅ Successful login	2025-04-07 15:08:13.849693	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
20	55	✅ TOTP verified successfully	2025-04-07 15:08:37.02091	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
21	55	❌ Failed login: Invalid password (1 recent)	2025-04-07 15:09:00.94601	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
22	55	❌ Failed login: Invalid password (2 recent)	2025-04-07 15:09:08.679228	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
23	55	❌ Failed login: Invalid password (3 recent)	2025-04-07 15:09:10.225275	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
24	55	❌ Failed login: Invalid password (4 recent)	2025-04-07 15:09:15.138944	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
25	55	❌ Failed login: Invalid password (5 recent)	2025-04-07 15:09:18.962248	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
26	55	🚨 Account temporarily locked due to multiple failed login attempts	2025-04-07 15:09:18.962248	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
27	22	✅ Successful login	2025-04-07 15:09:58.826699	192.168.2.110	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
28	22	❌ Failed TOTP verification (1)	2025-04-07 15:10:30.565004	192.168.2.110	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
29	22	✅ TOTP verified successfully	2025-04-07 15:10:40.913858	192.168.2.110	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
30	56	✅ Successful login	2025-04-07 15:18:48.000766	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
31	56	❌ Failed TOTP verification (1)	2025-04-07 15:19:18.212323	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
32	56	❌ Failed TOTP verification (2)	2025-04-07 15:19:20.678582	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
33	56	❌ Failed TOTP verification (3)	2025-04-07 15:19:22.365347	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
34	56	❌ Failed TOTP verification (4)	2025-04-07 15:19:24.526708	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
35	56	❌ Failed TOTP verification (5)	2025-04-07 15:19:27.737537	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
36	56	🚨 TOTP locked due to multiple failed attempts	2025-04-07 15:19:27.737537	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
37	56	✅ Successful login	2025-04-07 15:27:30.103613	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
38	22	✅ Successful login	2025-04-07 15:28:22.773018	192.168.2.110	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
39	22	✅ TOTP verified successfully	2025-04-07 15:28:36.534143	192.168.2.110	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
40	56	✅ Successful login	2025-04-07 15:32:09.666155	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
41	56	✅ Successful login	2025-04-07 16:14:34.57997	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
42	56	✅ TOTP verified successfully	2025-04-07 16:16:11.516601	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
43	22	❌ Failed login: Invalid password (1)	2025-04-07 16:16:33.858043	192.168.2.110	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
45	22	✅ TOTP verified successfully	2025-04-07 16:16:55.904616	192.168.2.110	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1219	57	✅ Successful login	2025-04-23 15:47:34.219757	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1234	56	❌ Tried reusing a previous password during reset	2025-04-23 16:59:59.132175	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1235	56	❌ Tried reusing a previous password during reset	2025-04-23 17:00:19.400894	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1236	56	🔐 Password reset successful	2025-04-23 17:00:42.702462	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1270	54	📨 TOTP reset link requested	2025-04-24 12:15:56.543416	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1271	54	📨 TOTP reset link requested	2025-04-24 14:41:26.161407	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1272	54	❌ Failed login: Invalid password (1)	2025-04-24 14:44:36.16597	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1273	54	✅ Successful login	2025-04-24 14:44:40.778599	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1274	54	✅ TOTP verified successfully	2025-04-24 14:44:55.025237	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1275	54	🔐 Logged in via WebAuthn (USB security key)	2025-04-24 14:45:02.935156	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1291	54	✅ Successful login	2025-04-24 18:28:32.471899	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1292	54	✅ TOTP verified successfully	2025-04-24 18:29:23.198553	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1293	54	🔐 Logged in via WebAuthn (USB security key)	2025-04-24 18:29:30.353695	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1294	54	📨 TOTP reset link requested	2025-04-24 18:47:08.29038	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1316	56	❌ Failed TOTP verification (1)	2025-04-24 19:57:38.767044	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1319	56	✅ Successful login	2025-04-24 19:58:54.811519	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1330	56	✅ TOTP verified successfully	2025-04-24 20:10:25.346469	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1333	56	📨 TOTP reset link requested	2025-04-24 21:11:36.022276	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1334	56	✅ TOTP reset after identity + trust check	2025-04-24 21:12:25.9894	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1335	56	✅ Successful login	2025-04-24 21:12:49.805614	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1336	56	✅ TOTP verified successfully	2025-04-24 21:13:25.88874	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1337	56	🔐 Logged in via WebAuthn (USB security key)	2025-04-24 21:13:32.882291	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1339	54	📧 Password reset requested	2025-04-25 09:21:25.940203	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1340	54	📧 Password reset requested	2025-04-25 09:41:00.217683	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1341	54	✅ Successful login	2025-04-25 09:44:14.826211	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1342	54	✅ TOTP verified successfully	2025-04-25 09:44:58.508444	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1343	54	🔐 Logged in via WebAuthn (USB security key)	2025-04-25 09:45:03.293265	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1359	54	✅ Password reset after MFA verification	2025-04-25 10:38:09.617333	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1378	54	❌ Attempted to reuse an old password during reset	2025-04-25 11:46:27.473736	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1385	54	❌ Failed TOTP verification (1)	2025-04-25 15:54:30.31612	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1386	54	✅ TOTP verified successfully	2025-04-25 15:54:48.931709	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1397	54	✅ WebAuthn reset verified	2025-04-25 17:09:15.599789	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1421	55	❌ Failed TOTP verification (1)	2025-04-25 17:31:54.519587	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1428	54	📧 Password reset requested	2025-04-25 18:14:23.864528	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1429	54	📧 Password reset requested	2025-04-25 18:17:12.140843	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1430	54	📧 Password reset requested	2025-04-25 20:16:46.123845	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1441	62	🔐 Logged in via WebAuthn (USB security key)	2025-04-25 20:36:09.091593	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
44	22	✅ Successful login	2025-04-07 16:16:40.127059	192.168.2.110	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
46	22	✅ Successful login	2025-04-07 16:40:42.983428	192.168.2.110	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
47	22	✅ TOTP verified successfully	2025-04-07 16:40:57.532275	192.168.2.110	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
48	55	✅ Successful login	2025-04-07 16:55:03.777362	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
49	55	❌ Failed TOTP verification (1)	2025-04-07 16:55:37.902416	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
50	55	✅ TOTP verified successfully	2025-04-07 16:55:46.305881	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
51	22	✅ Successful login	2025-04-07 16:56:43.694171	192.168.2.110	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
52	22	❌ Failed TOTP verification (2)	2025-04-07 16:57:03.05827	192.168.2.110	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
53	22	✅ TOTP verified successfully	2025-04-07 16:57:15.112854	192.168.2.110	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
54	54	✅ Successful login	2025-04-07 17:05:50.308185	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
55	54	✅ TOTP verified successfully	2025-04-07 17:06:15.576219	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
56	22	✅ Successful login	2025-04-07 17:17:03.120319	192.168.2.110	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
57	22	✅ TOTP verified successfully	2025-04-07 17:17:13.350831	192.168.2.110	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
58	22	✅ Successful login	2025-04-07 17:39:26.727639	192.168.2.110	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
59	22	✅ TOTP verified successfully	2025-04-07 17:39:44.898983	192.168.2.110	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
60	55	✅ Successful login	2025-04-07 17:40:41.243496	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
61	55	❌ Failed TOTP verification (2)	2025-04-07 17:40:48.561662	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
62	55	❌ Failed TOTP verification (3)	2025-04-07 17:40:51.573779	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
63	55	❌ Failed TOTP verification (4)	2025-04-07 17:40:54.050797	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
64	55	❌ Failed TOTP verification (5)	2025-04-07 17:40:55.701801	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
65	55	🚨 TOTP temporarily locked after multiple failed attempts	2025-04-07 17:40:55.701801	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
66	55	✅ TOTP verified successfully	2025-04-07 17:43:15.882136	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
67	55	❌ Failed login: Invalid password (6)	2025-04-07 17:51:59.846655	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
68	55	🚨 Account temporarily locked due to failed login attempts	2025-04-07 17:51:59.846655	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
69	22	✅ Successful login	2025-04-07 17:58:19.259707	192.168.2.110	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
70	22	✅ TOTP verified successfully	2025-04-07 17:58:42.088785	192.168.2.110	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
71	55	✅ Successful login	2025-04-07 18:12:37.714783	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
72	55	❌ Failed TOTP verification (6)	2025-04-07 18:12:52.422572	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
73	55	🚨 TOTP temporarily locked after multiple failed attempts	2025-04-07 18:12:52.422572	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
74	22	✅ Successful login	2025-04-07 18:14:00.033307	192.168.2.110	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
75	22	✅ TOTP verified successfully	2025-04-07 18:14:25.490345	192.168.2.110	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
76	55	❌ Failed TOTP verification (7)	2025-04-07 18:18:48.818016	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
77	55	🚨 TOTP temporarily locked after multiple failed attempts	2025-04-07 18:18:48.818016	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
78	22	✅ Successful login	2025-04-07 19:04:20.504915	192.168.2.110	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
79	22	✅ TOTP verified successfully	2025-04-07 19:04:40.476137	192.168.2.110	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
80	56	❌ Failed login: Invalid password (1)	2025-04-07 19:06:08.855544	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
81	56	❌ Failed login: Invalid password (2)	2025-04-07 19:06:11.654158	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
82	56	❌ Failed login: Invalid password (3)	2025-04-07 19:06:12.795141	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
83	56	❌ Failed login: Invalid password (4)	2025-04-07 19:06:14.116149	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
84	56	❌ Failed login: Invalid password (5)	2025-04-07 19:06:15.163903	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
85	56	🚨 Account temporarily locked due to failed login attempts	2025-04-07 19:06:15.163903	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
86	55	✅ Successful login	2025-04-07 19:08:01.312352	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
87	55	✅ TOTP verified successfully	2025-04-07 19:08:21.161186	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
88	22	✅ Successful login	2025-04-07 19:24:35.680676	192.168.2.110	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
89	22	✅ TOTP verified successfully	2025-04-07 19:24:48.877064	192.168.2.110	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
90	55	✅ Successful login	2025-04-07 19:40:23.860978	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
91	55	✅ TOTP verified successfully	2025-04-07 19:40:41.770752	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
92	55	Withdrawal of 892.0 RWF	2025-04-07 19:42:19.549561	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	34.7341, 135.7414	f	1
93	22	✅ Successful login	2025-04-07 19:42:36.713666	192.168.2.110	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
94	22	✅ TOTP verified successfully	2025-04-07 19:42:47.36903	192.168.2.110	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
95	55	❌ Failed login: Invalid password (7)	2025-04-07 19:44:34.041945	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
96	55	🚨 Account temporarily locked due to failed login attempts	2025-04-07 19:44:34.041945	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
97	54	✅ Successful login	2025-04-07 19:46:08.653541	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
98	54	✅ TOTP verified successfully	2025-04-07 19:46:39.159522	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
99	55	✅ Successful login	2025-04-07 20:02:24.894681	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
100	55	✅ TOTP verified successfully	2025-04-07 20:02:43.395179	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
101	55	Transfer of 100.0 RWF	2025-04-07 20:03:21.142202	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	34.7341, 135.7414	f	1
102	22	✅ Successful login	2025-04-07 20:04:03.543245	192.168.2.110	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
103	22	✅ TOTP verified successfully	2025-04-07 20:04:21.779766	192.168.2.110	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
104	55	Withdrawal of 200.0 RWF	2025-04-07 20:13:16.029677	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	34.7341, 135.7414	f	1
105	22	✅ Successful login	2025-04-08 11:13:11.392877	192.168.2.110	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
106	22	❌ Failed TOTP verification (1)	2025-04-08 11:13:29.936268	192.168.2.110	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
107	22	✅ TOTP verified successfully	2025-04-08 11:13:45.238607	192.168.2.110	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
108	54	✅ Successful login	2025-04-08 11:24:42.550598	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
109	54	✅ TOTP verified successfully	2025-04-08 11:24:57.229269	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
110	54	🧾 Agent deposited 100.0 RWF to Gabriel (0783437740)	2025-04-08 11:26:18.744748	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Location not available	f	1
111	54	🔁 Agent transferred 100.0 RWF to Dary (0782409658)	2025-04-08 11:28:47.21217	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Location not available	f	1
112	22	✅ Successful login	2025-04-08 11:29:37.169541	192.168.2.110	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
113	22	✅ TOTP verified successfully	2025-04-08 11:29:53.540799	192.168.2.110	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
114	54	💸 Agent withdrew 100.0 RWF from own float	2025-04-08 11:31:28.489765	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Location not available	f	1
115	55	✅ Successful login	2025-04-08 11:42:29.551532	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
116	55	✅ TOTP verified successfully	2025-04-08 11:42:41.493409	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
117	54	✅ Successful login	2025-04-08 11:47:59.908019	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
118	54	✅ TOTP verified successfully	2025-04-08 11:48:14.782073	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
119	56	✅ Successful login	2025-04-08 11:49:12.633004	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
120	56	✅ TOTP verified successfully	2025-04-08 11:49:24.157622	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
121	22	✅ Successful login	2025-04-08 11:50:08.271537	192.168.2.110	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
122	22	✅ TOTP verified successfully	2025-04-08 11:50:28.477764	192.168.2.110	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
123	54	✅ Successful login	2025-04-08 11:58:19.325922	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
124	54	✅ TOTP verified successfully	2025-04-08 11:58:37.505592	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
125	56	✅ Successful login	2025-04-08 12:13:31.792979	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
126	56	✅ TOTP verified successfully	2025-04-08 12:13:43.822315	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
127	56	Withdrawal of 1000.0 RWF	2025-04-08 12:14:17.828179	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0		f	1
128	22	✅ Successful login	2025-04-08 12:14:40.000304	192.168.2.110	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
130	54	✅ Successful login	2025-04-08 12:15:13.370294	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
129	22	✅ TOTP verified successfully	2025-04-08 12:14:48.298636	192.168.2.110	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
131	54	✅ TOTP verified successfully	2025-04-08 12:15:29.076649	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
132	54	✅ Approved withdrawal of 1000.0 RWF for User 56	2025-04-08 12:15:44.310822	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Agent location	f	1
133	55	✅ Successful login	2025-04-08 15:13:56.205492	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
134	55	❌ Failed TOTP verification (1)	2025-04-08 15:14:14.046882	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
135	55	✅ TOTP verified successfully	2025-04-08 15:14:25.697651	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
136	55	Withdrawal of 100.0 RWF	2025-04-08 15:15:50.84976	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0		f	1
137	54	✅ Successful login	2025-04-08 15:16:10.276207	192.168.2.110	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
138	54	✅ TOTP verified successfully	2025-04-08 15:16:20.313285	192.168.2.110	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
139	54	❌ Rejected withdrawal of 100.0 RWF for User 55	2025-04-08 15:17:59.759956	192.168.2.110	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Agent location	t	1
140	22	✅ Successful login	2025-04-08 15:18:31.859899	192.168.2.110	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
141	22	✅ TOTP verified successfully	2025-04-08 15:19:11.103207	192.168.2.110	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
142	54	✅ Successful login	2025-04-08 15:24:36.520612	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
143	54	✅ TOTP verified successfully	2025-04-08 15:25:28.759098	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
144	54	🗑️ Deleted SIM ICCID: 8901417788523574	2025-04-08 15:37:02.428997	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
145	22	✅ Successful login	2025-04-08 15:37:20.309547	192.168.2.110	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
146	22	✅ TOTP verified successfully	2025-04-08 15:37:41.121869	192.168.2.110	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
147	54	⚠️ Suspended SIM ICCID: 8901695622409502	2025-04-08 15:38:09.039045	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
148	54	✅ Successful login	2025-04-08 15:53:19.323179	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
149	54	✅ TOTP verified successfully	2025-04-08 15:53:36.426821	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
150	54	✅ Successful login	2025-04-08 16:09:43.952499	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
151	54	✅ TOTP verified successfully	2025-04-08 16:09:56.281911	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
152	54	🔄 Re-activated suspended SIM ICCID: 8901695622409502	2025-04-08 16:11:10.273968	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
153	22	✅ Successful login	2025-04-08 16:11:44.913969	192.168.2.110	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
154	22	❌ Failed TOTP verification (2)	2025-04-08 16:12:01.208263	192.168.2.110	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
155	22	✅ TOTP verified successfully	2025-04-08 16:12:09.12621	192.168.2.110	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
156	54	✅ Successful login	2025-04-08 17:17:08.969573	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
157	54	✅ TOTP verified successfully	2025-04-08 17:20:08.298563	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
1220	57	✅ TOTP verified successfully	2025-04-23 15:47:50.056125	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
159	54	✅ Successful login	2025-04-08 17:43:22.459544	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
160	54	✅ TOTP verified successfully	2025-04-08 17:43:38.901342	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
1237	57	📧 Password reset requested	2025-04-23 17:11:30.656199	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1238	56	📧 Password reset requested	2025-04-23 17:13:03.785307	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
163	54	✅ Successful login	2025-04-08 18:00:35.396356	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
164	54	✅ TOTP verified successfully	2025-04-08 18:01:45.175585	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
165	54	🔄 SIM swapped for SWP_1744070543: 8901695622409502 ➡️ 8901554522579976	2025-04-08 18:02:23.379428	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
166	56	✅ Successful login	2025-04-08 18:03:54.395865	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
167	56	✅ TOTP verified successfully	2025-04-08 18:04:17.181226	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
168	22	✅ Successful login	2025-04-08 18:04:47.444036	192.168.2.110	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
169	22	✅ TOTP verified successfully	2025-04-08 18:05:05.756059	192.168.2.110	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
170	54	✅ Successful login	2025-04-08 18:06:45.00126	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
1239	56	🔐 Password reset successful	2025-04-23 17:13:44.195995	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
171	54	❌ Failed TOTP verification (1)	2025-04-08 18:07:06.083104	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
172	54	❌ Failed TOTP verification (2)	2025-04-08 18:07:22.981897	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
173	54	✅ TOTP verified successfully	2025-04-08 18:07:44.30516	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
174	54	✅ Successful login	2025-04-08 18:24:38.436151	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
175	54	✅ TOTP verified successfully	2025-04-08 18:24:51.387097	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
176	22	✅ Successful login	2025-04-08 18:26:36.650897	192.168.2.110	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
177	22	✅ TOTP verified successfully	2025-04-08 18:26:57.66647	192.168.2.110	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
178	54	✅ Successful login	2025-04-08 18:43:39.010756	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
179	54	✅ TOTP verified successfully	2025-04-08 18:43:48.246465	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
180	54	🔄 SIM swapped for 0782409658: 8901162439021695 ➡️ 8901569377994495	2025-04-08 18:57:46.187182	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
181	22	✅ Successful login	2025-04-08 18:59:38.471616	192.168.2.110	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
182	22	✅ TOTP verified successfully	2025-04-08 19:00:07.195915	192.168.2.110	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
183	54	✅ Successful login	2025-04-08 19:01:05.931436	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
184	54	✅ TOTP verified successfully	2025-04-08 19:01:15.65929	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
185	54	✅ Successful login	2025-04-08 19:17:22.140365	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
186	54	✅ TOTP verified successfully	2025-04-08 19:17:37.464592	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
187	54	📲 Activated SIM ICCID: 8901946394441134	2025-04-08 19:19:48.059097	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
188	22	✅ Successful login	2025-04-08 19:20:21.760644	192.168.2.110	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
189	22	✅ TOTP verified successfully	2025-04-08 19:20:40.483225	192.168.2.110	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
190	54	🔄 SIM swapped for 0788599992: 8901946394441134 ➡️ 8901497901168751	2025-04-08 19:22:46.835866	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
191	54	✅ Successful login	2025-04-08 19:32:45.83337	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
192	54	✅ TOTP verified successfully	2025-04-08 19:32:58.20039	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
193	22	✅ Successful login	2025-04-08 19:51:30.151341	192.168.2.110	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
194	22	✅ TOTP verified successfully	2025-04-08 19:51:48.246551	192.168.2.110	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
195	22	🔁 Reversed transfer of 1000.0 RWF from user 54 back to 55 (TX #171)	2025-04-08 20:04:10.277267	192.168.2.110	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Headquarters	t	1
196	22	🔁 Reversed transfer of 1000.0 RWF from user 54 back to 55 (TX #171)	2025-04-08 20:04:40.440099	192.168.2.110	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Headquarters	t	1
197	22	❌ Failed login: Invalid password (1)	2025-04-08 20:07:57.064655	192.168.2.110	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
198	22	✅ Successful login	2025-04-08 20:08:05.569615	192.168.2.110	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
199	22	✅ TOTP verified successfully	2025-04-08 20:08:12.513774	192.168.2.110	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
200	56	✅ Successful login	2025-04-08 20:11:05.936644	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
201	56	✅ TOTP verified successfully	2025-04-08 20:11:22.925314	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
202	56	Transfer of 2000.0 RWF	2025-04-08 20:11:57.746242	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0		f	1
203	22	🔁 Reversal initiated: TX #190 — 2000.0 RWF back to sender	2025-04-08 20:12:27.306761	192.168.2.110	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Headquarters	t	1
204	22	✅ Successful login	2025-04-09 15:42:09.025261	192.168.2.110	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
205	22	❌ Failed TOTP verification (1)	2025-04-09 15:42:28.932063	192.168.2.110	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
206	22	✅ TOTP verified successfully	2025-04-09 15:42:42.10399	192.168.2.110	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
207	22	✅ Successful login	2025-04-09 16:05:29.077114	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
208	22	✅ TOTP verified successfully	2025-04-09 16:06:12.579909	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
209	55	✅ Successful login	2025-04-09 16:08:21.529171	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
210	55	✅ TOTP verified successfully	2025-04-09 16:10:23.425944	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
211	55	Withdrawal of 2000.0 RWF	2025-04-09 16:12:12.305027	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	34.7341, 135.7414	f	1
212	54	✅ Successful login	2025-04-09 16:12:49.998357	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
213	54	✅ TOTP verified successfully	2025-04-09 16:13:38.109728	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
214	54	❌ Rejected withdrawal of 2000.0 RWF for User 55	2025-04-09 16:14:11.269309	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Agent location	t	1
215	22	✅ Successful login	2025-04-10 15:11:27.278159	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
216	22	✅ TOTP verified successfully	2025-04-10 15:11:48.110254	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
217	22	✅ Successful login	2025-04-11 09:49:20.237765	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
218	22	✅ TOTP verified successfully	2025-04-11 09:49:36.804561	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
219	55	✅ Successful login	2025-04-11 09:52:35.205095	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
220	55	✅ TOTP verified successfully	2025-04-11 09:52:48.791454	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
221	56	✅ Successful login	2025-04-11 09:55:10.869665	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
222	56	✅ TOTP verified successfully	2025-04-11 09:55:21.628093	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
223	22	❌ Failed login: Invalid password (1)	2025-04-11 10:08:20.827469	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
224	22	✅ Successful login	2025-04-11 10:08:26.524314	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
225	22	✅ TOTP verified successfully	2025-04-11 10:08:46.5827	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
226	56	✅ Successful login	2025-04-11 10:09:14.017276	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
227	55	✅ Successful login	2025-04-11 10:09:28.261588	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
228	55	✅ TOTP verified successfully	2025-04-11 10:09:40.154454	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
229	55	Transfer of 2000.0 RWF	2025-04-11 10:10:22.362135	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	34.7308, 135.7480	f	1
230	22	🔁 Reversal initiated: TX #193 — 2000.0 RWF back to sender	2025-04-11 10:10:48.960021	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Headquarters	t	1
231	22	✅ Successful login	2025-04-11 10:25:11.10572	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
232	22	✅ TOTP verified successfully	2025-04-11 10:25:19.470823	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
233	55	✅ Successful login	2025-04-11 10:36:43.402445	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
234	55	✅ TOTP verified successfully	2025-04-11 10:36:53.988616	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
235	55	Transfer of 200.0 RWF	2025-04-11 10:37:20.348883	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	34.7308, 135.7480	f	1
236	22	🔁 Reversal initiated: TX #195 — 200.0 RWF back to sender	2025-04-11 10:37:46.424031	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Headquarters	t	1
237	22	✅ Successful login	2025-04-11 10:41:35.483365	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
238	22	✅ TOTP verified successfully	2025-04-11 10:41:53.371953	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
239	55	Transfer of 50.0 RWF	2025-04-11 10:43:14.248706	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	34.7308, 135.7480	f	1
240	22	🔁 Reversal initiated: TX #197 — 50.0 RWF back to sender	2025-04-11 10:43:41.422268	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Headquarters	t	1
241	55	✅ Reversal completed: 50.0 RWF refunded to sender for TX #197	2025-04-11 10:43:51.460945	System	Auto Processor	Headquarters	f	1
242	55	Transfer of 1150.0 RWF	2025-04-11 10:46:29.434924	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	34.7308, 135.7480	f	1
243	22	✅ Successful login	2025-04-11 10:47:27.783313	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
287	56	✅ Successful login	2025-04-11 15:50:29.492301	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
244	22	✅ TOTP verified successfully	2025-04-11 10:47:45.067382	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
245	56	✅ Successful login	2025-04-11 10:48:13.73739	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
246	56	✅ TOTP verified successfully	2025-04-11 10:48:23.818135	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
247	22	🔁 Reversal initiated: TX #199 — 1150.0 RWF back to sender	2025-04-11 10:48:57.746149	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Headquarters	t	1
248	55	✅ Reversal completed: 1150.0 RWF refunded to sender for TX #199	2025-04-11 10:49:07.783235	System	Auto Processor	Headquarters	f	1
249	54	✅ Successful login	2025-04-11 10:58:26.075546	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
250	54	✅ TOTP verified successfully	2025-04-11 10:58:45.023297	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
251	54	🧾 Agent deposited 100.0 RWF to Gabriel (0783437740)	2025-04-11 11:04:54.666083	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	34.7308, 135.7480	f	1
252	56	✅ Successful login	2025-04-11 11:05:28.623909	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
1221	57	✅ Successful login	2025-04-23 16:02:30.210009	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1222	57	✅ TOTP verified successfully	2025-04-23 16:02:48.131032	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1240	56	📧 Password reset requested	2025-04-23 17:17:40.213626	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1241	56	🔐 Password reset successful	2025-04-23 17:18:01.735388	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1255	56	❌ Failed login: Invalid password (1)	2025-04-24 09:49:22.071542	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1256	56	❌ Failed login: Invalid password (2)	2025-04-24 09:49:27.218723	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1257	54	✅ Successful login	2025-04-24 09:49:59.899549	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1258	54	✅ TOTP verified successfully	2025-04-24 09:50:20.022718	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1259	54	⚠️ Client-side WebAuthn failure: User cancelled or did not interact with WebAuthn prompt in time. (NotAllowedError: The operation either timed out or was not allowed. See: https://www.w3.org/TR/webauthn-2/#sctn-privacy-considerations-client.)	2025-04-24 09:50:27.957364	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1260	56	📨 TOTP reset link requested	2025-04-24 09:50:45.014127	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1261	56	📧 Password reset requested	2025-04-24 09:54:23.552798	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1262	56	🔐 Password reset successful	2025-04-24 09:55:13.860212	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1263	54	✅ Successful login	2025-04-24 09:55:44.919686	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1276	54	📨 TOTP reset link requested	2025-04-24 15:03:30.304094	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1295	54	⚠️ TOTP reset denied due to low trust score	2025-04-24 18:50:55.976354	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1296	54	⚠️ TOTP reset denied due to low trust score	2025-04-24 18:53:07.348051	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1317	56	📨 TOTP reset link requested	2025-04-24 19:57:54.936046	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1322	56	📨 TOTP reset link requested	2025-04-24 20:05:13.009326	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1326	56	🔐 Logged in via WebAuthn (USB security key)	2025-04-24 20:07:21.376842	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1327	56	📨 TOTP reset link requested	2025-04-24 20:08:59.057799	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1328	56	✅ TOTP reset after identity + trust check	2025-04-24 20:09:26.378214	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1344	54	📧 Password reset requested	2025-04-25 10:02:44.256224	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1361	54	✅ Successful login	2025-04-25 10:39:18.070037	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1379	54	❌ Attempted to reuse an old password during reset	2025-04-25 11:46:32.666255	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1387	54	⚠️ Client-side WebAuthn failure: User cancelled or did not interact with WebAuthn prompt in time. (NotAllowedError: The operation either timed out or was not allowed. See: https://www.w3.org/TR/webauthn-2/#sctn-privacy-considerations-client.)	2025-04-25 16:00:16.323603	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1398	54	📨 WebAuthn reset link requested	2025-04-25 17:17:18.361107	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1399	54	✅ WebAuthn reset verified	2025-04-25 17:17:56.636296	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1400	54	📨 WebAuthn reset link requested	2025-04-25 17:19:43.322619	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1401	54	✅ WebAuthn reset verified	2025-04-25 17:20:38.843139	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1402	54	✅ Successful login	2025-04-25 17:21:28.935033	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1403	54	✅ TOTP verified successfully	2025-04-25 17:21:56.323343	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1404	54	🔐 Logged in via WebAuthn (cross-device passkey)	2025-04-25 17:22:23.662087	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1405	54	❌ Failed login: Invalid password (5)	2025-04-25 17:22:41.377243	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1406	54	🚨 Account temporarily locked due to failed login attempts	2025-04-25 17:22:41.377243	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1417	54	✅ TOTP verified successfully	2025-04-25 17:27:49.471088	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1424	22	✅ Successful login	2025-04-25 17:33:12.590288	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
253	56	✅ TOTP verified successfully	2025-04-11 11:05:37.612061	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
254	54	✅ Successful login	2025-04-11 11:14:07.291025	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
255	54	✅ TOTP verified successfully	2025-04-11 11:14:16.652299	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
256	54	🔁 Agent transferred 200.0 RWF to Gabriel (0783437740)	2025-04-11 11:14:48.365676	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	34.7308, 135.7480	f	1
257	22	✅ Successful login	2025-04-11 11:15:58.360024	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
258	22	✅ TOTP verified successfully	2025-04-11 11:16:16.385961	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
259	56	✅ Successful login	2025-04-11 11:21:33.818859	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
260	56	✅ TOTP verified successfully	2025-04-11 11:21:46.369563	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
261	56	Withdrawal of 1000.0 RWF	2025-04-11 11:23:13.102002	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	34.7315, 135.7347	f	1
262	54	✅ Successful login	2025-04-11 11:29:22.016082	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
263	54	✅ TOTP verified successfully	2025-04-11 11:29:38.562196	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
264	54	⏳ Withdrawal request of 1000.0 RWF for User 56 expired	2025-04-11 11:29:59.867251	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Agent location	t	1
265	22	✅ Successful login	2025-04-11 14:52:27.78709	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
266	22	✅ TOTP verified successfully	2025-04-11 14:52:52.107622	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
267	22	✅ Successful login	2025-04-11 14:55:25.5046	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
268	22	✅ TOTP verified successfully	2025-04-11 14:55:43.096809	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
269	22	✅ Successful login	2025-04-11 15:04:07.883025	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
270	22	✅ TOTP verified successfully	2025-04-11 15:04:23.103834	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
271	56	✅ Successful login	2025-04-11 15:05:16.533892	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
272	56	✅ TOTP verified successfully	2025-04-11 15:05:36.102254	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
273	56	✅ Successful login	2025-04-11 15:16:58.567482	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
274	56	✅ TOTP verified successfully	2025-04-11 15:17:12.717685	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
275	22	✅ Successful login	2025-04-11 15:17:51.86477	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
276	22	✅ TOTP verified successfully	2025-04-11 15:18:06.857515	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
277	22	✅ Successful login	2025-04-11 15:24:22.76152	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
278	22	✅ TOTP verified successfully	2025-04-11 15:24:39.439268	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
279	56	✅ Successful login	2025-04-11 15:25:22.17475	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
280	56	✅ TOTP verified successfully	2025-04-11 15:25:36.471374	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
281	56	✅ Successful login	2025-04-11 15:44:07.182015	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
282	56	✅ TOTP verified successfully	2025-04-11 15:44:14.42129	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
283	55	✅ Successful login	2025-04-11 15:45:56.502411	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
284	55	✅ TOTP verified successfully	2025-04-11 15:46:06.797429	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
285	55	✅ Successful login	2025-04-11 15:46:24.878095	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
286	55	✅ TOTP verified successfully	2025-04-11 15:46:41.412824	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
288	56	❌ Failed TOTP verification (1)	2025-04-11 15:50:40.582951	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
289	56	✅ TOTP verified successfully	2025-04-11 15:50:52.716057	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
290	56	❌ Failed TOTP verification (2)	2025-04-11 15:52:21.76408	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
291	56	✅ TOTP verified successfully	2025-04-11 15:52:41.821365	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
292	56	✅ TOTP verified successfully	2025-04-11 15:53:07.476682	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
293	56	✅ Successful login	2025-04-11 16:15:06.578413	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
294	56	✅ TOTP verified successfully	2025-04-11 16:15:17.124379	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
295	56	✅ TOTP verified successfully	2025-04-11 16:26:40.10166	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
296	56	✅ Successful login	2025-04-11 16:37:40.54961	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
297	56	✅ TOTP verified successfully	2025-04-11 16:37:56.052509	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
298	56	✅ Successful login	2025-04-11 17:02:27.33702	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
299	56	✅ TOTP verified successfully	2025-04-11 17:02:39.010888	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
300	56	✅ Successful login	2025-04-11 17:23:11.77523	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
301	56	✅ TOTP verified successfully	2025-04-11 17:23:26.6146	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
302	56	❌ Failed TOTP verification (3)	2025-04-11 17:26:24.759975	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	t	1
303	56	✅ TOTP verified successfully	2025-04-11 17:26:48.13974	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
304	56	✅ Successful login	2025-04-11 17:29:11.638428	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
305	56	✅ TOTP verified successfully	2025-04-11 17:29:20.151059	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
306	56	✅ TOTP verified successfully	2025-04-11 17:33:38.055125	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
307	56	✅ Successful login	2025-04-11 17:37:51.062925	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
308	56	✅ TOTP verified successfully	2025-04-11 17:38:06.892086	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
309	56	✅ Successful login	2025-04-11 17:41:54.665998	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
310	56	✅ TOTP verified successfully	2025-04-11 17:42:06.273504	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
311	56	✅ Successful login	2025-04-11 17:55:56.106359	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
312	56	✅ TOTP verified successfully	2025-04-11 17:56:12.805662	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
313	22	✅ Successful login	2025-04-11 18:03:10.925372	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
314	22	✅ TOTP verified successfully	2025-04-11 18:03:28.710444	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
315	22	❌ Failed login: Invalid password (2)	2025-04-11 18:18:57.205323	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
316	\N	❌ Failed login: Unknown identifier test@admin	2025-04-11 18:19:04.077621	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	t	1
317	22	✅ Successful login	2025-04-11 18:19:23.368775	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
318	22	✅ TOTP verified successfully	2025-04-11 18:19:39.231685	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
319	56	✅ Successful login	2025-04-11 18:52:50.549502	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
320	56	✅ TOTP verified successfully	2025-04-11 18:53:08.350984	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
321	22	✅ Successful login	2025-04-11 18:59:32.94869	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
322	22	✅ TOTP verified successfully	2025-04-11 18:59:41.238142	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
323	22	✅ Successful login	2025-04-11 19:24:17.542219	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
324	22	✅ TOTP verified successfully	2025-04-11 19:24:39.700819	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
325	22	✅ Successful login	2025-04-11 19:31:45.023663	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
326	22	❌ Failed TOTP verification (1)	2025-04-11 19:32:00.065976	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
327	22	✅ TOTP verified successfully	2025-04-11 19:32:09.972302	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
328	22	✅ TOTP verified successfully	2025-04-11 19:41:52.398429	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
329	22	✅ Successful login	2025-04-11 19:52:04.709482	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
330	22	✅ TOTP verified successfully	2025-04-11 19:52:18.881645	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
331	55	✅ Successful login	2025-04-11 19:59:54.292135	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
332	55	✅ TOTP verified successfully	2025-04-11 20:00:09.286341	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
333	56	✅ Successful login	2025-04-11 20:17:03.21634	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
334	56	✅ TOTP verified successfully	2025-04-11 20:17:14.755369	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
335	55	✅ Successful login	2025-04-11 20:24:56.121677	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
336	55	✅ TOTP verified successfully	2025-04-11 20:25:10.126594	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
337	56	✅ Successful login	2025-04-11 20:40:42.904635	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
338	56	✅ TOTP verified successfully	2025-04-11 20:40:55.835043	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
339	55	✅ Successful login	2025-04-11 20:50:30.831257	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
340	55	✅ TOTP verified successfully	2025-04-11 20:50:48.353485	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
341	56	✅ Successful login	2025-04-11 20:59:05.483608	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
342	56	✅ TOTP verified successfully	2025-04-11 20:59:17.778522	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
343	22	✅ Successful login	2025-04-11 21:39:37.11835	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
344	22	✅ TOTP verified successfully	2025-04-11 21:40:08.459071	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
345	22	✅ TOTP verified successfully	2025-04-11 21:42:16.22821	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
346	22	✅ Successful login	2025-04-11 22:13:24.189407	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
347	22	✅ TOTP verified successfully	2025-04-11 22:13:44.130302	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
348	22	✅ TOTP verified successfully	2025-04-11 22:17:27.621173	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
349	56	✅ Successful login	2025-04-11 22:32:36.063137	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
350	56	✅ TOTP verified successfully	2025-04-11 22:32:47.184018	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
351	56	✅ TOTP verified successfully	2025-04-11 22:33:23.563879	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
352	56	✅ TOTP verified successfully	2025-04-11 22:41:18.654602	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
353	56	✅ TOTP verified successfully	2025-04-11 22:41:55.282518	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
354	54	✅ Successful login	2025-04-11 22:42:37.380669	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
355	54	✅ TOTP verified successfully	2025-04-11 22:42:49.451214	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
356	54	✅ Successful login	2025-04-11 22:50:32.979024	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
357	54	✅ TOTP verified successfully	2025-04-11 22:50:46.813871	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
358	54	✅ Successful login	2025-04-11 22:51:55.083465	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
359	54	✅ TOTP verified successfully	2025-04-11 22:52:10.337005	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
360	54	✅ Successful login	2025-04-11 22:54:57.406474	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
361	54	❌ Failed TOTP verification (1)	2025-04-11 22:55:11.224878	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
362	54	✅ TOTP verified successfully	2025-04-11 22:55:26.169432	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
363	54	✅ Successful login	2025-04-11 22:58:29.589213	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
364	54	✅ TOTP verified successfully	2025-04-11 22:58:43.914808	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
365	54	✅ Successful login	2025-04-11 23:00:05.975482	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
366	54	✅ TOTP verified successfully	2025-04-11 23:00:16.498169	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
367	54	✅ Successful login	2025-04-11 23:32:31.180473	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
368	54	✅ TOTP verified successfully	2025-04-11 23:32:49.789632	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
369	54	❌ Failed TOTP verification (2)	2025-04-11 23:37:56.348458	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
370	54	✅ TOTP verified successfully	2025-04-11 23:38:09.646652	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
371	54	✅ Successful login	2025-04-11 23:38:54.966987	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
372	54	✅ TOTP verified successfully	2025-04-11 23:39:06.898806	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
373	54	✅ Successful login	2025-04-11 23:51:14.129456	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
374	54	✅ TOTP verified successfully	2025-04-11 23:51:24.93196	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
375	54	✅ TOTP verified successfully	2025-04-11 23:57:16.197404	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
376	56	✅ Successful login	2025-04-12 11:04:41.187456	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
377	56	❌ Failed TOTP verification (1)	2025-04-12 11:05:07.235388	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
378	56	✅ TOTP verified successfully	2025-04-12 11:05:23.610525	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
380	22	✅ TOTP verified successfully	2025-04-12 11:15:17.306351	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
381	22	✅ Successful login	2025-04-12 11:23:04.537549	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
382	22	✅ TOTP verified successfully	2025-04-12 11:23:29.232393	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
383	22	❌ Failed login: Invalid password (1)	2025-04-12 12:14:55.172103	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
384	22	❌ Failed login: Invalid password (2)	2025-04-12 12:15:02.63317	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
385	22	✅ Successful login	2025-04-12 12:16:25.54622	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
386	22	✅ TOTP verified successfully	2025-04-12 12:16:37.358193	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
387	22	✅ Successful login	2025-04-12 12:31:41.462854	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
388	22	✅ TOTP verified successfully	2025-04-12 12:31:58.623986	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
389	22	✅ TOTP verified successfully	2025-04-12 12:45:36.75765	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
390	22	✅ Successful login	2025-04-12 12:48:58.547566	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
391	22	✅ TOTP verified successfully	2025-04-12 12:49:08.113715	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
392	22	❌ Failed TOTP verification (1)	2025-04-12 12:53:30.620883	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	t	1
393	22	✅ TOTP verified successfully	2025-04-12 12:53:39.814939	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
394	22	✅ Successful login	2025-04-12 13:05:49.254733	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
395	22	✅ TOTP verified successfully	2025-04-12 13:05:58.224224	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
396	22	✅ Successful login	2025-04-12 13:22:32.101859	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
397	22	✅ TOTP verified successfully	2025-04-12 13:22:38.882795	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
398	56	✅ Successful login	2025-04-12 13:26:05.814125	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
399	56	✅ TOTP verified successfully	2025-04-12 13:26:18.524316	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
400	56	❌ Failed TOTP verification (2)	2025-04-12 13:26:45.779705	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
401	56	✅ TOTP verified successfully	2025-04-12 13:27:04.885057	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
402	55	❌ Failed login: Invalid password (1)	2025-04-12 13:27:44.569337	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
403	55	✅ Successful login	2025-04-12 13:27:49.710361	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
404	55	✅ TOTP verified successfully	2025-04-12 13:27:59.425161	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
405	54	✅ Successful login	2025-04-12 13:29:54.255345	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
406	54	❌ Failed TOTP verification (1)	2025-04-12 13:30:06.687068	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
407	54	✅ TOTP verified successfully	2025-04-12 13:30:16.027063	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
408	56	❌ Failed login: Invalid password (1)	2025-04-12 13:40:22.248982	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
409	56	✅ Successful login	2025-04-12 13:40:27.097404	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
410	56	✅ TOTP verified successfully	2025-04-12 13:40:45.899166	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
411	56	✅ TOTP verified successfully	2025-04-12 13:40:58.807409	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
412	56	❌ Failed TOTP verification (3)	2025-04-12 13:41:18.460733	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
413	56	❌ Failed TOTP verification (4)	2025-04-12 13:41:20.886284	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
414	56	❌ Failed TOTP verification (5)	2025-04-12 13:41:23.272473	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
415	56	🚨 TOTP temporarily locked after multiple failed attempts	2025-04-12 13:41:23.272473	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
416	55	✅ Successful login	2025-04-12 13:42:01.465695	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
417	55	✅ TOTP verified successfully	2025-04-12 13:42:09.643956	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
418	22	✅ Successful login	2025-04-12 13:43:45.65044	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
419	22	✅ TOTP verified successfully	2025-04-12 13:44:10.954748	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
420	56	✅ Successful login	2025-04-12 13:55:35.063806	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
421	56	✅ TOTP verified successfully	2025-04-12 13:55:50.261788	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
422	55	✅ Successful login	2025-04-12 13:56:18.625067	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
423	55	❌ Failed TOTP verification (1)	2025-04-12 13:56:30.098601	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
424	55	✅ TOTP verified successfully	2025-04-12 13:56:40.247206	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
425	22	✅ Successful login	2025-04-12 14:32:18.331207	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
426	22	✅ TOTP verified successfully	2025-04-12 14:32:37.276909	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
427	57	✅ Successful login	2025-04-12 14:35:05.872695	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
428	57	✅ TOTP verified successfully	2025-04-12 14:35:52.781476	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
429	57	✅ TOTP verified successfully	2025-04-12 14:49:15.180568	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
430	57	✅ Successful login	2025-04-12 15:07:25.339685	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
431	57	✅ TOTP verified successfully	2025-04-12 15:07:39.802914	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
432	54	✅ Successful login	2025-04-12 15:10:35.78963	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
433	54	✅ TOTP verified successfully	2025-04-12 15:10:49.127782	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
434	57	✅ TOTP verified successfully	2025-04-12 15:14:08.640453	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
435	22	✅ Successful login	2025-04-12 15:26:20.868745	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
436	22	✅ TOTP verified successfully	2025-04-12 15:26:45.95245	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
437	22	✅ Successful login	2025-04-12 15:32:42.415661	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
438	22	✅ TOTP verified successfully	2025-04-12 15:33:07.776887	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
439	57	✅ Successful login	2025-04-12 15:53:02.831105	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
440	57	✅ TOTP verified successfully	2025-04-12 15:53:13.997707	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
441	57	✅ TOTP verified successfully	2025-04-12 15:55:29.041774	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
442	57	✅ Successful login	2025-04-12 16:02:47.78522	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
443	57	✅ TOTP verified successfully	2025-04-12 16:02:59.241517	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
444	57	✅ Successful login	2025-04-12 16:20:17.035882	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
445	57	✅ TOTP verified successfully	2025-04-12 16:20:37.88964	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
446	57	✅ TOTP verified successfully	2025-04-12 16:31:57.092511	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
447	57	✅ Successful login	2025-04-12 16:36:02.813078	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
448	57	✅ TOTP verified successfully	2025-04-12 16:36:14.234385	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
449	57	✅ Successful login	2025-04-12 17:01:11.971466	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
450	57	✅ TOTP verified successfully	2025-04-12 17:01:24.400111	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
451	57	✅ Successful login	2025-04-12 17:34:08.345489	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
452	57	✅ TOTP verified successfully	2025-04-12 17:34:25.775471	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
453	57	🔐 Logged in via WebAuthn (USB security key)	2025-04-12 17:35:27.560244	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
454	22	✅ Successful login	2025-04-12 17:35:46.825056	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
455	22	✅ TOTP verified successfully	2025-04-12 17:36:06.633704	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
456	22	🔐 Logged in via WebAuthn (platform authenticator (fingerprint))	2025-04-12 17:36:10.791324	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
457	57	✅ Successful login	2025-04-12 17:46:30.632073	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
458	57	✅ TOTP verified successfully	2025-04-12 17:46:45.554117	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
459	57	🔐 Logged in via WebAuthn (USB security key)	2025-04-12 17:46:53.44192	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
460	55	✅ Successful login	2025-04-12 17:47:07.65295	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
461	55	✅ TOTP verified successfully	2025-04-12 17:47:22.932395	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
462	55	🔐 Logged in via WebAuthn (cross-device passkey (e.g. phone))	2025-04-12 17:47:29.171737	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
463	22	❌ Failed login: Invalid password (3)	2025-04-12 17:47:48.610023	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
464	22	✅ Successful login	2025-04-12 17:47:55.472934	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
465	22	✅ TOTP verified successfully	2025-04-12 17:48:10.696528	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
466	22	🔐 Logged in via WebAuthn (cross-device passkey (e.g. phone))	2025-04-12 17:48:14.936223	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
467	54	✅ Successful login	2025-04-12 17:52:14.298716	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
468	54	✅ TOTP verified successfully	2025-04-12 17:52:26.858415	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
469	54	🔐 Logged in via WebAuthn (cross-device passkey)	2025-04-12 17:52:30.790558	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
470	22	✅ Successful login	2025-04-12 17:53:12.7167	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
471	22	✅ TOTP verified successfully	2025-04-12 17:53:21.773089	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
472	22	🔐 Logged in via WebAuthn (cross-device passkey)	2025-04-12 17:53:25.319502	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
473	56	✅ Successful login	2025-04-12 18:09:45.789202	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
474	56	✅ TOTP verified successfully	2025-04-12 18:10:06.390099	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
475	56	❌ WebAuthn login failed (unknown method)	2025-04-12 18:10:12.575506	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
476	56	🔐 Logged in via WebAuthn (cross-device passkey)	2025-04-12 18:14:32.712413	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
477	57	✅ Successful login	2025-04-12 18:32:16.122133	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
478	57	✅ TOTP verified successfully	2025-04-12 18:32:28.204927	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
479	57	❌ WebAuthn authentication failed	2025-04-12 18:32:34.09114	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
480	57	❌ WebAuthn authentication failed	2025-04-12 18:36:01.562651	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
481	57	❌ WebAuthn authentication failed	2025-04-12 18:36:27.500042	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
482	57	✅ Successful login	2025-04-12 18:36:58.491662	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
483	57	✅ TOTP verified successfully	2025-04-12 18:37:08.973582	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
484	57	❌ WebAuthn authentication failed	2025-04-12 18:37:13.251272	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
485	55	✅ Successful login	2025-04-12 18:37:49.586005	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
486	55	❌ Failed TOTP verification (2)	2025-04-12 18:37:59.93881	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
487	55	✅ TOTP verified successfully	2025-04-12 18:38:09.909071	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
488	55	❌ WebAuthn authentication failed	2025-04-12 18:38:14.177168	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
489	55	❌ WebAuthn authentication failed	2025-04-12 18:42:16.256199	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	t	1
490	55	✅ Successful login	2025-04-12 18:45:43.074873	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
491	55	✅ TOTP verified successfully	2025-04-12 18:45:57.049792	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
492	55	❌ WebAuthn authentication failed	2025-04-12 18:46:02.245707	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	t	1
493	55	❌ WebAuthn authentication failed	2025-04-12 18:50:46.316391	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	t	1
494	55	❌ WebAuthn authentication failed: AuthenticationResponse.from_dict called with non-Mapping data of type<class 'list'>	2025-04-12 18:55:00.780654	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	t	1
495	55	🔐 Logged in via WebAuthn (cross-device passkey)	2025-04-12 18:55:51.384297	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
496	22	✅ Successful login	2025-04-12 18:57:14.524766	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
497	22	✅ TOTP verified successfully	2025-04-12 18:57:39.37202	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
498	22	🔐 Logged in via WebAuthn (cross-device passkey)	2025-04-12 18:57:42.787415	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
499	22	✅ Successful login	2025-04-12 18:58:37.251387	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
500	22	✅ TOTP verified successfully	2025-04-12 18:58:52.892597	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
501	22	🔐 Logged in via WebAuthn (cross-device passkey)	2025-04-12 18:59:09.220092	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
502	57	✅ Successful login	2025-04-14 08:52:14.786768	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
503	57	✅ TOTP verified successfully	2025-04-14 08:52:37.234528	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
504	57	🔐 Logged in via WebAuthn (USB security key)	2025-04-14 08:53:25.427657	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
505	22	❌ Failed login: Invalid password (1)	2025-04-14 08:54:48.673227	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
506	22	✅ Successful login	2025-04-14 08:54:55.149931	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
507	22	✅ TOTP verified successfully	2025-04-14 08:55:11.366826	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
508	22	🔐 Logged in via WebAuthn (cross-device passkey)	2025-04-14 08:55:17.974475	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
509	57	✅ Successful login	2025-04-14 08:58:02.793548	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
510	57	✅ TOTP verified successfully	2025-04-14 08:58:17.857776	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
511	57	🔐 Logged in via WebAuthn (USB security key)	2025-04-14 08:58:29.292818	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
512	57	✅ TOTP verified successfully	2025-04-14 09:00:16.268688	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
513	57	🔐 Logged in via WebAuthn (USB security key)	2025-04-14 09:00:31.479572	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
514	22	✅ Successful login	2025-04-14 09:03:18.264268	192.168.2.115	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
515	22	✅ TOTP verified successfully	2025-04-14 09:03:40.247002	192.168.2.115	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
516	57	🔐 Logged in via WebAuthn (USB security key)	2025-04-14 09:07:51.457407	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
517	22	✅ Successful login	2025-04-14 09:13:51.704559	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
518	22	✅ TOTP verified successfully	2025-04-14 09:15:09.704675	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
519	22	🔐 Logged in via WebAuthn (cross-device passkey)	2025-04-14 09:15:14.324504	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
520	22	🛠️ Assigned role 'agent' to user Bio test (0787408913)	2025-04-14 09:15:36.060798	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Headquarters	f	1
521	22	✅ Successful login	2025-04-14 09:56:42.969466	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
522	22	✅ TOTP verified successfully	2025-04-14 09:56:53.916225	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
523	22	🔐 Logged in via WebAuthn (cross-device passkey)	2025-04-14 09:57:00.051538	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
524	22	👁️ Viewed profile of Bio test (0787408913)	2025-04-14 09:57:40.526858	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Headquarters	f	1
525	22	🚫 Suspended user pathos muta (0787832379) and marked for deletion.	2025-04-14 09:58:13.503901	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Headquarters	t	1
562	57	❌ Failed login: Invalid password (4)	2025-04-14 11:55:52.320776	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
526	22	✅ Verified and reactivated user pathos muta (0787832379)	2025-04-14 09:58:49.369525	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Headquarters	f	1
527	22	✏️ Edited user Pathos Mut (0787832379) — Fields updated: first_name, last_name	2025-04-14 10:00:04.90065	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Headquarters	f	1
528	22	📱 Admin generated SIM: 8901183383756135 with mobile 0787955541	2025-04-14 10:00:47.007484	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Headquarters	f	1
529	56	❌ Failed login: Invalid password (1)	2025-04-14 10:04:10.800044	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
530	56	❌ Failed login: Invalid password (2)	2025-04-14 10:04:14.284274	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
531	56	❌ Failed login: Invalid password (3)	2025-04-14 10:04:15.84379	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
532	56	❌ Failed login: Invalid password (4)	2025-04-14 10:04:16.91399	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
533	56	❌ Failed login: Invalid password (5)	2025-04-14 10:04:18.029936	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
534	56	🚨 Account temporarily locked due to failed login attempts	2025-04-14 10:04:18.029936	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
535	22	🔓 Unlocked user account for Gabriel Darwin (SWP_1744070543)	2025-04-14 10:05:10.453225	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Admin Panel	f	1
536	22	✅ Successful login	2025-04-14 10:12:25.921903	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
537	22	❌ Failed TOTP verification (1)	2025-04-14 10:12:38.848926	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
538	22	✅ TOTP verified successfully	2025-04-14 10:12:49.558407	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
539	22	🔐 Logged in via WebAuthn (cross-device passkey)	2025-04-14 10:12:54.065754	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
540	22	💸 Funded agent Pathos (0787832379) with 5000.0 RWF from HQ Wallet	2025-04-14 10:16:59.749389	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	{"lat": 34.7308032, "lng": 135.7479936}	f	1
541	55	❌ Failed login: Invalid password (1)	2025-04-14 11:25:09.338658	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
542	55	❌ Failed login: Invalid password (2)	2025-04-14 11:25:10.31732	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
543	55	❌ Failed login: Invalid password (3)	2025-04-14 11:31:36.045738	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	t	1
544	55	❌ Failed login: Invalid password (4)	2025-04-14 11:31:41.30368	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	t	1
545	55	❌ Failed login: Invalid password (5)	2025-04-14 11:31:45.577708	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	t	1
546	55	🚨 Account temporarily locked due to failed login attempts	2025-04-14 11:31:45.577708	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	t	1
547	54	✅ Successful login	2025-04-14 11:32:58.463667	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
548	54	❌ Failed TOTP verification (1)	2025-04-14 11:33:07.533155	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	t	1
549	54	❌ Failed TOTP verification (2)	2025-04-14 11:33:09.457394	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	t	1
550	54	❌ Failed TOTP verification (3)	2025-04-14 11:33:10.193899	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	t	1
551	54	❌ Failed TOTP verification (4)	2025-04-14 11:33:11.120522	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	t	1
552	54	❌ Failed TOTP verification (5)	2025-04-14 11:33:12.323257	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	t	1
553	54	🚨 TOTP temporarily locked after multiple failed attempts	2025-04-14 11:33:12.323257	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	t	1
554	22	✅ Successful login	2025-04-14 11:34:16.453731	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
555	22	✅ TOTP verified successfully	2025-04-14 11:34:28.600184	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
556	22	🔐 Logged in via WebAuthn (cross-device passkey)	2025-04-14 11:34:32.950069	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
557	22	🔓 Unlocked user account for Pathos Mut (0787832379)	2025-04-14 11:47:39.553536	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Admin Panel	f	1
558	57	❌ Failed login: Invalid password (1)	2025-04-14 11:48:01.095827	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
559	57	❌ Failed login: Invalid password (2)	2025-04-14 11:48:05.416665	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
560	57	✅ Successful login	2025-04-14 11:55:33.672463	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
561	57	❌ Failed login: Invalid password (3)	2025-04-14 11:55:49.026779	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
563	57	❌ Failed login: Invalid password (5)	2025-04-14 11:55:55.449535	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
564	57	🚨 Account temporarily locked due to failed login attempts	2025-04-14 11:55:55.449535	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
565	22	✅ Successful login	2025-04-14 12:00:47.63059	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
566	22	❌ Failed TOTP verification (2)	2025-04-14 12:01:06.665409	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
567	22	✅ TOTP verified successfully	2025-04-14 12:01:21.891811	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
568	22	🔐 Logged in via WebAuthn (cross-device passkey)	2025-04-14 12:01:25.508643	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
569	56	❌ Failed login: Invalid password (6)	2025-04-14 12:11:59.508782	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
570	56	🚨 Account temporarily locked due to failed login attempts	2025-04-14 12:11:59.508782	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
571	22	✅ Successful login	2025-04-14 12:19:16.426913	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
572	22	✅ TOTP verified successfully	2025-04-14 12:24:08.551946	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
573	22	🔐 Logged in via WebAuthn (cross-device passkey)	2025-04-14 12:24:12.567319	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
574	22	❌ Failed login: Invalid password (2)	2025-04-14 14:56:33.226941	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
575	22	✅ Successful login	2025-04-14 14:56:42.562802	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
576	22	✅ TOTP verified successfully	2025-04-14 14:57:08.054909	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
577	22	🔐 Logged in via WebAuthn (cross-device passkey)	2025-04-14 14:57:12.644199	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
578	56	❌ Failed login: Invalid password (7)	2025-04-14 15:31:22.375757	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
579	56	🚨 Account temporarily locked due to failed login attempts	2025-04-14 15:31:22.375757	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
580	54	✅ Successful login	2025-04-14 15:33:42.694249	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
581	54	❌ Failed TOTP verification (6)	2025-04-14 15:33:59.732382	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
582	54	🚨 TOTP temporarily locked after multiple failed attempts	2025-04-14 15:33:59.732382	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
583	57	✅ Successful login	2025-04-14 16:09:12.801985	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
584	57	✅ TOTP verified successfully	2025-04-14 16:09:29.586768	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
585	57	✅ Successful login	2025-04-14 16:32:40.803458	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
586	57	✅ TOTP verified successfully	2025-04-14 16:33:27.740565	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
587	57	❌ Failed WebAuthn attempt (1)	2025-04-14 16:33:36.173672	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
588	57	❌ Failed WebAuthn attempt (2)	2025-04-14 16:41:34.087001	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
589	57	✅ Successful login	2025-04-14 16:48:10.242757	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
590	57	✅ TOTP verified successfully	2025-04-14 16:48:24.170965	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
591	57	❌ Failed WebAuthn attempt (3)	2025-04-14 16:48:29.503768	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
592	57	❌ Failed WebAuthn attempt (4)	2025-04-14 16:50:17.074884	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
593	57	✅ TOTP verified successfully	2025-04-14 16:53:36.09846	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
594	57	✅ Successful login	2025-04-14 17:11:35.353938	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
595	57	✅ TOTP verified successfully	2025-04-14 17:11:46.822789	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
596	57	❌ Failed WebAuthn attempt (5)	2025-04-14 17:21:39.474035	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
597	57	🚨 WebAuthn lockout triggered due to repeated failures	2025-04-14 17:21:39.474035	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
598	22	✅ Successful login	2025-04-14 17:27:13.773265	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
599	22	✅ TOTP verified successfully	2025-04-14 17:27:26.11872	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
600	22	❌ Failed WebAuthn attempt (1)	2025-04-14 17:27:30.958473	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
601	22	❌ Failed WebAuthn attempt (2)	2025-04-14 17:31:06.858264	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
602	22	❌ Failed WebAuthn attempt (3)	2025-04-14 17:32:36.999959	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
603	22	❌ Failed WebAuthn attempt (4)	2025-04-14 17:38:06.112579	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
604	22	✅ Successful login	2025-04-14 17:42:29.439537	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
605	22	✅ TOTP verified successfully	2025-04-14 17:42:42.255071	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
606	22	❌ Failed WebAuthn attempt (5)	2025-04-14 17:42:45.53308	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
607	22	🚨 WebAuthn lockout triggered due to repeated failures	2025-04-14 17:42:45.53308	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
608	54	✅ Successful login	2025-04-14 17:47:10.473108	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
609	54	✅ TOTP verified successfully	2025-04-14 17:47:22.861324	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
610	55	✅ Successful login	2025-04-14 17:48:21.047847	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
611	55	✅ TOTP verified successfully	2025-04-14 17:48:37.801507	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
612	55	❌ Failed WebAuthn attempt (1)	2025-04-14 17:48:42.212855	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	t	1
613	55	❌ Failed WebAuthn attempt (2)	2025-04-14 17:55:32.138895	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	t	1
614	56	✅ Successful login	2025-04-14 18:03:43.591464	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
615	56	✅ TOTP verified successfully	2025-04-14 18:04:07.294218	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
616	56	❌ Failed WebAuthn attempt (1)	2025-04-14 18:04:11.574423	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	t	1
617	56	❌ Failed WebAuthn attempt (2)	2025-04-14 18:09:42.633597	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	t	1
618	54	✅ Successful login	2025-04-14 18:16:11.617522	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
619	54	✅ TOTP verified successfully	2025-04-14 18:16:24.241345	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
620	54	❌ Failed WebAuthn attempt (1)	2025-04-14 18:16:28.754825	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	t	1
621	54	❌ Failed WebAuthn attempt (2)	2025-04-14 18:18:56.320328	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	t	1
622	55	✅ Successful login	2025-04-14 18:21:55.987747	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
623	55	✅ TOTP verified successfully	2025-04-14 18:22:07.988399	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
624	55	❌ Failed WebAuthn attempt (3)	2025-04-14 18:22:11.877886	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	t	1
625	55	❌ Failed WebAuthn attempt (4)	2025-04-14 18:27:03.665544	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	t	1
626	55	🔐 Logged in via WebAuthn (cross-device passkey)	2025-04-14 18:28:08.291627	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
627	22	✅ Successful login	2025-04-14 18:32:22.416228	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
628	22	✅ TOTP verified successfully	2025-04-14 18:32:37.301427	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
629	56	✅ Successful login	2025-04-14 18:34:11.240963	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
630	56	✅ TOTP verified successfully	2025-04-14 18:34:25.641036	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
631	56	❌ Failed WebAuthn attempt (3)	2025-04-14 18:34:29.484736	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
632	56	❌ Failed WebAuthn attempt (4)	2025-04-14 18:40:39.912483	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
633	54	✅ Successful login	2025-04-14 18:43:49.625585	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
634	54	✅ TOTP verified successfully	2025-04-14 18:43:58.854969	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
635	54	❌ Failed WebAuthn attempt (3)	2025-04-14 18:44:01.725539	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
636	54	❌ Failed WebAuthn attempt (4)	2025-04-14 18:44:58.710808	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
637	54	✅ Successful login	2025-04-14 18:52:33.310708	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
638	54	✅ TOTP verified successfully	2025-04-14 18:52:43.297799	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
639	54	❌ Failed WebAuthn attempt (5)	2025-04-14 18:52:47.649066	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
640	54	🚨 WebAuthn lockout triggered due to repeated failures	2025-04-14 18:52:47.649066	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
641	56	✅ Successful login	2025-04-14 18:57:05.657687	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
642	57	✅ Successful login	2025-04-14 18:57:37.235445	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
643	57	✅ TOTP verified successfully	2025-04-14 18:57:46.64557	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
644	57	❌ Failed WebAuthn attempt (6)	2025-04-14 18:57:53.647751	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
645	57	🚨 WebAuthn lockout triggered due to repeated failures	2025-04-14 18:57:53.647751	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
646	55	✅ Successful login	2025-04-14 19:01:31.733385	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
647	55	✅ TOTP verified successfully	2025-04-14 19:01:49.810464	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
648	55	❌ Failed WebAuthn attempt (5)	2025-04-14 19:01:53.739354	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
649	55	🚨 WebAuthn lockout triggered due to repeated failures	2025-04-14 19:01:53.739354	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
650	56	✅ Successful login	2025-04-14 19:07:02.834033	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
651	56	✅ TOTP verified successfully	2025-04-14 19:07:15.473885	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
652	56	❌ Failed WebAuthn attempt (5)	2025-04-14 19:07:18.630314	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
653	56	❌ Failed WebAuthn attempt (6)	2025-04-14 19:11:09.062112	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
654	56	❌ Failed WebAuthn attempt (7)	2025-04-14 19:13:41.529322	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
655	56	❌ Failed WebAuthn attempt (8)	2025-04-14 19:16:01.853154	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
656	56	❌ Failed WebAuthn attempt (9)	2025-04-14 19:16:41.842398	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
657	56	❌ Failed WebAuthn attempt (10)	2025-04-14 19:17:43.163837	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
658	56	❌ Failed WebAuthn attempt (11)	2025-04-14 19:20:49.031259	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
659	56	✅ Successful login	2025-04-14 19:22:28.038539	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
660	56	✅ TOTP verified successfully	2025-04-14 19:22:38.710025	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
661	56	❌ Failed WebAuthn attempt (12)	2025-04-14 19:22:42.029098	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
662	56	❌ Failed WebAuthn attempt (13)	2025-04-14 19:24:56.658383	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
663	56	❌ Failed WebAuthn attempt (14)	2025-04-14 19:27:43.995397	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
664	56	❌ Failed WebAuthn attempt (15)	2025-04-14 19:29:09.054527	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
665	56	❌ Failed WebAuthn attempt (16)	2025-04-14 19:30:42.368245	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
666	56	❌ Failed WebAuthn attempt (17)	2025-04-14 19:36:37.425809	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	t	1
667	55	✅ Successful login	2025-04-14 19:43:59.606633	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
668	55	✅ TOTP verified successfully	2025-04-14 19:44:17.519914	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
669	55	❌ Failed WebAuthn attempt (6)	2025-04-14 19:44:21.34856	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	t	1
670	54	✅ Successful login	2025-04-14 19:59:34.112697	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
671	54	✅ TOTP verified successfully	2025-04-14 19:59:43.820303	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
672	55	❌ Failed login: Invalid password (6)	2025-04-14 20:14:56.630464	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	t	1
673	55	🚨 Account temporarily locked due to failed login attempts	2025-04-14 20:14:56.630464	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	t	1
674	54	✅ Successful login	2025-04-14 20:15:27.608656	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
675	54	✅ TOTP verified successfully	2025-04-14 20:16:09.7049	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
676	54	✅ TOTP verified successfully	2025-04-14 20:19:05.308897	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
677	54	❌ Failed WebAuthn attempt (6)	2025-04-14 20:23:49.675398	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	t	1
678	54	✅ Successful login	2025-04-14 20:27:56.769801	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
679	54	✅ TOTP verified successfully	2025-04-14 20:28:19.385612	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
680	22	✅ Successful login	2025-04-14 20:45:01.384517	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
681	22	✅ TOTP verified successfully	2025-04-14 20:45:15.749093	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
682	22	✅ Successful login	2025-04-14 20:59:59.065194	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
683	22	✅ TOTP verified successfully	2025-04-14 21:00:14.584229	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
684	22	✅ TOTP verified successfully	2025-04-14 21:00:51.343228	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
685	56	✅ Successful login	2025-04-14 21:13:17.458914	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
686	56	❌ Failed TOTP verification (1)	2025-04-14 21:13:24.780913	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
687	56	❌ Failed TOTP verification (2)	2025-04-14 21:13:28.995715	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
688	56	❌ Failed TOTP verification (3)	2025-04-14 21:13:31.401242	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
689	56	❌ Failed TOTP verification (4)	2025-04-14 21:13:33.784142	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
690	56	❌ Failed TOTP verification (5)	2025-04-14 21:13:35.789318	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
691	56	🚨 TOTP temporarily locked after multiple failed attempts	2025-04-14 21:13:35.789318	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
692	56	✅ Successful login	2025-04-15 08:31:07.704557	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
693	56	✅ TOTP verified successfully	2025-04-15 08:31:24.020477	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
694	56	❌ Failed TOTP verification (1)	2025-04-15 08:32:34.442783	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
695	56	✅ TOTP verified successfully	2025-04-15 08:32:49.157663	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
696	55	✅ Successful login	2025-04-15 08:52:08.451397	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
697	55	✅ TOTP verified successfully	2025-04-15 08:53:26.064416	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
698	55	❌ Failed TOTP verification (1)	2025-04-15 08:54:08.252581	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	t	1
699	55	✅ TOTP verified successfully	2025-04-15 08:54:37.439497	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
700	56	✅ Successful login	2025-04-15 09:05:57.407579	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
701	56	✅ TOTP verified successfully	2025-04-15 09:06:08.006224	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
702	56	❌ Failed WebAuthn attempt (1)	2025-04-15 09:06:12.392892	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
703	56	✅ Successful login	2025-04-15 09:10:53.446173	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
704	56	❌ Failed TOTP verification (2)	2025-04-15 09:11:12.365572	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
705	56	✅ TOTP verified successfully	2025-04-15 09:11:21.187149	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
706	57	✅ Successful login	2025-04-15 09:12:35.580096	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
707	57	✅ TOTP verified successfully	2025-04-15 09:12:44.508002	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
708	54	✅ Successful login	2025-04-15 09:27:09.84525	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
709	54	✅ TOTP verified successfully	2025-04-15 09:27:25.32922	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
710	54	✅ TOTP verified successfully	2025-04-15 09:28:06.96092	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
711	54	❌ Failed WebAuthn attempt (1)	2025-04-15 09:28:12.923258	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
712	54	❌ Failed WebAuthn attempt (2)	2025-04-15 09:30:40.043601	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
713	54	❌ Failed WebAuthn attempt (3)	2025-04-15 09:38:05.363309	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
714	56	✅ Successful login	2025-04-15 09:48:56.875486	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
715	56	✅ TOTP verified successfully	2025-04-15 09:49:09.777663	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
716	56	❌ Failed WebAuthn attempt (2)	2025-04-15 09:52:53.564287	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	t	1
717	56	✅ Successful login	2025-04-15 10:07:38.041489	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
718	56	✅ TOTP verified successfully	2025-04-15 10:08:08.079629	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
719	54	✅ Successful login	2025-04-15 10:30:20.611745	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
720	54	✅ TOTP verified successfully	2025-04-15 10:30:35.038787	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
721	54	🔐 Logged in via WebAuthn (USB security key)	2025-04-15 10:30:43.936458	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
722	56	✅ Successful login	2025-04-15 10:42:11.954948	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
723	56	✅ TOTP verified successfully	2025-04-15 10:42:26.944053	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
724	56	✅ Successful login	2025-04-15 10:43:44.491189	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
725	56	✅ TOTP verified successfully	2025-04-15 10:43:56.50474	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
726	56	✅ Successful login	2025-04-15 10:54:27.633578	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
727	56	✅ TOTP verified successfully	2025-04-15 10:54:41.182904	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
728	56	❌ WebAuthn login failed (3)	2025-04-15 10:55:39.835601	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	t	1
729	56	❌ WebAuthn login failed (4)	2025-04-15 10:58:42.73079	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	t	1
730	56	❌ WebAuthn login failed (5)	2025-04-15 11:03:40.497198	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	t	1
731	57	✅ Successful login	2025-04-15 11:04:52.405155	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
732	57	✅ TOTP verified successfully	2025-04-15 11:05:06.833913	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
733	57	✅ Successful login	2025-04-15 11:27:41.839265	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
734	57	✅ TOTP verified successfully	2025-04-15 11:27:55.057763	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
735	57	✅ Successful login	2025-04-15 11:42:46.384001	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
736	57	❌ Failed TOTP verification (1)	2025-04-15 11:43:00.566914	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
737	57	✅ TOTP verified successfully	2025-04-15 11:43:08.421768	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
738	57	🔐 Logged in via WebAuthn (USB security key)	2025-04-15 11:44:14.794226	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
739	57	✅ Successful login	2025-04-15 11:49:02.602509	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
740	57	✅ TOTP verified successfully	2025-04-15 11:49:15.202458	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
741	57	❌ WebAuthn login failed (1)	2025-04-15 11:57:48.172025	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
742	57	❌ WebAuthn login failed (2)	2025-04-15 12:01:03.15385	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
743	57	❌ WebAuthn login failed (3)	2025-04-15 12:03:57.961076	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	t	1
744	57	❌ Failed login: Invalid password (1)	2025-04-15 12:08:51.435331	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
745	57	✅ Successful login	2025-04-15 12:08:57.423266	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
746	57	✅ TOTP verified successfully	2025-04-15 12:09:13.370759	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
747	57	❌ WebAuthn login failed (4)	2025-04-15 12:09:18.35258	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	t	1
748	57	🔐 Logged in via WebAuthn (USB security key)	2025-04-15 12:11:03.048539	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
749	57	✅ Successful login	2025-04-15 12:24:30.40056	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
750	57	✅ TOTP verified successfully	2025-04-15 12:24:46.537016	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
751	57	🔐 Logged in via WebAuthn (USB security key)	2025-04-15 12:34:49.938518	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
752	57	✅ Successful login	2025-04-15 12:37:42.644595	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
753	57	✅ TOTP verified successfully	2025-04-15 12:37:55.336369	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
754	57	❌ Failed WebAuthn assertion (AuthenticationResponse.from_dict called with non-Mapping data of type<class 'list'>) (5)	2025-04-15 12:52:13.203649	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
755	57	🚨 WebAuthn temporarily locked after multiple failed attempts	2025-04-15 12:52:13.203649	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
756	56	✅ Successful login	2025-04-15 12:54:05.902608	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
757	56	✅ TOTP verified successfully	2025-04-15 12:54:18.120517	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
758	56	❌ Failed WebAuthn assertion (AuthenticationResponse.from_dict called with non-Mapping data of type<class 'list'>) (6)	2025-04-15 12:54:21.636091	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
759	56	🚨 WebAuthn temporarily locked after multiple failed attempts	2025-04-15 12:54:21.636091	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
760	57	✅ Successful login	2025-04-15 13:10:27.792016	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
761	57	✅ TOTP verified successfully	2025-04-15 13:10:43.994189	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
762	57	✅ Successful login	2025-04-15 13:12:59.881777	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
763	57	✅ TOTP verified successfully	2025-04-15 13:13:15.653558	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
764	57	🔐 Logged in via WebAuthn (USB security key)	2025-04-15 13:13:20.336238	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
765	57	✅ Successful login	2025-04-15 13:16:20.539817	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
766	57	✅ TOTP verified successfully	2025-04-15 13:16:37.376364	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
767	57	🔐 Logged in via WebAuthn (USB security key)	2025-04-15 13:16:42.447116	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
768	57	✅ Successful login	2025-04-15 13:19:50.190807	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
769	57	✅ TOTP verified successfully	2025-04-15 13:20:05.918101	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
770	57	✅ Successful login	2025-04-15 14:36:16.176345	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
771	57	✅ TOTP verified successfully	2025-04-15 14:36:27.521993	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
772	57	✅ Successful login	2025-04-15 14:51:34.922138	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
773	57	✅ TOTP verified successfully	2025-04-15 14:51:46.107344	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
774	57	✅ Successful login	2025-04-15 15:08:47.677664	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
775	57	✅ TOTP verified successfully	2025-04-15 15:09:07.244996	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
776	57	✅ Successful login	2025-04-15 15:16:13.9881	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
777	57	✅ TOTP verified successfully	2025-04-15 15:16:28.313803	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
778	57	🔐 Logged in via WebAuthn (USB security key)	2025-04-15 15:16:33.932586	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
779	22	✅ Successful login	2025-04-15 15:29:25.227852	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
780	22	✅ TOTP verified successfully	2025-04-15 15:29:42.73813	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
781	22	✅ TOTP verified successfully	2025-04-15 15:30:17.118586	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
782	22	🔐 Logged in via WebAuthn (USB security key)	2025-04-15 15:30:21.983689	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
783	22	✅ Successful login	2025-04-15 15:45:40.590565	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
784	22	✅ TOTP verified successfully	2025-04-15 15:45:54.158836	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
785	22	🔥 SERVER ERROR during WebAuthn assertion	2025-04-15 15:46:00.962216	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
786	22	❌ Failed WebAuthn attempt (1)	2025-04-15 15:46:56.222886	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
787	22	❌ Failed WebAuthn assertion (AuthenticationResponse.from_dict called with non-Mapping data of type<class 'list'>) (2)	2025-04-15 15:55:09.722433	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	t	1
788	22	❌ Failed WebAuthn assertion (AuthenticationResponse.from_dict called with non-Mapping data of type<class 'list'>) (3)	2025-04-15 15:59:12.232522	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	t	1
789	22	❌ Failed login: Invalid password (1)	2025-04-15 16:12:00.316202	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
790	57	✅ Successful login	2025-04-15 16:12:10.118519	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
791	57	❌ Failed TOTP verification (2)	2025-04-15 16:12:30.149321	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
792	57	✅ TOTP verified successfully	2025-04-15 16:12:38.806341	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
793	57	❌ Failed WebAuthn assertion (AuthenticationResponse.from_dict called with non-Mapping data of type<class 'list'>) (6)	2025-04-15 16:12:44.326747	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
794	57	❌ Failed WebAuthn assertion (AuthenticationResponse.from_dict called with non-Mapping data of type<class 'list'>) (7)	2025-04-15 16:15:13.280571	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
795	57	❌ Failed WebAuthn assertion (AuthenticationResponse.from_dict called with non-Mapping data of type<class 'list'>) (8)	2025-04-15 16:19:11.181147	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
796	57	✅ Successful login	2025-04-15 16:30:43.547235	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
797	57	✅ TOTP verified successfully	2025-04-15 16:30:55.358055	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
798	57	❌ Failed WebAuthn assertion (AuthenticationResponse.from_dict called with non-Mapping data of type<class 'list'>) (9)	2025-04-15 16:38:39.932465	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
799	57	🔐 Logged in via WebAuthn (USB security key)	2025-04-15 16:45:05.993051	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
800	57	✅ Successful login	2025-04-15 16:48:23.059785	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
801	57	✅ TOTP verified successfully	2025-04-15 16:48:39.637148	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
802	57	🔐 Logged in via WebAuthn (USB security key)	2025-04-15 16:48:48.944808	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
803	57	✅ Successful login	2025-04-15 16:57:37.239644	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
804	57	✅ TOTP verified successfully	2025-04-15 16:57:48.220451	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
805	57	❌ Failed WebAuthn assertion (AuthenticationResponse.from_dict called with non-Mapping data of type<class 'list'>) (10)	2025-04-15 16:59:36.963364	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
806	57	🔐 Logged in via WebAuthn (USB security key)	2025-04-15 17:02:01.72829	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
807	57	✅ Successful login	2025-04-15 17:05:01.946766	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
808	57	✅ TOTP verified successfully	2025-04-15 17:05:15.340433	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
809	57	🔐 Logged in via WebAuthn (USB security key)	2025-04-15 17:05:20.413472	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
810	57	🔐 Logged in via WebAuthn (USB security key)	2025-04-15 17:06:17.282493	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
811	57	✅ Successful login	2025-04-15 17:10:37.178365	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
812	57	✅ TOTP verified successfully	2025-04-15 17:10:53.777677	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
813	57	🔐 Logged in via WebAuthn (USB security key)	2025-04-15 17:11:00.598107	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
814	22	✅ Successful login	2025-04-15 17:11:59.568026	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
815	22	✅ TOTP verified successfully	2025-04-15 17:12:16.03501	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
816	22	🔐 Logged in via WebAuthn (USB security key)	2025-04-15 17:12:22.26519	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
817	54	✅ Successful login	2025-04-15 17:17:08.810489	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
818	54	✅ TOTP verified successfully	2025-04-15 17:17:21.473071	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
819	54	🔐 Logged in via WebAuthn (USB security key)	2025-04-15 17:17:27.836226	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
820	54	✅ Successful login	2025-04-15 17:18:10.885316	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
821	54	✅ TOTP verified successfully	2025-04-15 17:18:36.971613	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
822	54	🔐 Logged in via WebAuthn (USB security key)	2025-04-15 17:27:32.554712	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
823	22	✅ Successful login	2025-04-15 17:29:39.620351	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
824	22	✅ TOTP verified successfully	2025-04-15 17:29:53.744953	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
825	22	🔐 Logged in via WebAuthn (USB security key)	2025-04-15 17:29:59.813161	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
826	56	✅ Successful login	2025-04-15 17:30:27.650421	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
827	56	✅ TOTP verified successfully	2025-04-15 17:30:44.651805	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
828	56	✅ Successful login	2025-04-15 17:33:11.653925	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
829	56	✅ TOTP verified successfully	2025-04-15 17:33:25.797991	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
830	54	✅ Successful login	2025-04-15 17:33:50.948516	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
831	54	✅ TOTP verified successfully	2025-04-15 17:34:06.962528	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
832	54	🔐 Logged in via WebAuthn (USB security key)	2025-04-15 17:34:12.366103	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
833	56	❌ Failed login: Invalid password (1)	2025-04-15 17:37:03.220026	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
834	56	✅ Successful login	2025-04-15 17:37:09.382719	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
835	56	✅ TOTP verified successfully	2025-04-15 17:37:23.740224	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
836	56	✅ TOTP verified successfully	2025-04-15 17:39:06.54036	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
837	56	🔐 Logged in via WebAuthn (cross-device passkey)	2025-04-15 17:39:13.110051	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
838	56	❌ Failed login: Invalid password (2)	2025-04-15 17:46:07.419728	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
839	56	✅ Successful login	2025-04-15 17:46:12.876559	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
840	56	✅ TOTP verified successfully	2025-04-15 17:46:26.539275	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
841	56	🔐 Logged in via WebAuthn (cross-device passkey)	2025-04-15 17:46:51.738104	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
842	56	✅ Successful login	2025-04-15 17:48:40.543923	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
843	56	✅ TOTP verified successfully	2025-04-15 17:48:51.546817	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
844	56	🔐 Logged in via WebAuthn (cross-device passkey)	2025-04-15 17:48:55.219101	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
845	57	✅ Successful login	2025-04-15 17:50:59.391337	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
846	57	❌ Failed TOTP verification (3)	2025-04-15 17:51:24.516699	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
847	57	❌ Failed TOTP verification (4)	2025-04-15 17:51:31.194531	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
848	57	❌ Failed TOTP verification (5)	2025-04-15 17:51:34.230873	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
849	57	🚨 TOTP temporarily locked after multiple failed attempts	2025-04-15 17:51:34.230873	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
850	54	✅ Successful login	2025-04-15 17:52:15.983882	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
851	54	✅ TOTP verified successfully	2025-04-15 17:52:28.370645	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
852	54	🔐 Logged in via WebAuthn (USB security key)	2025-04-15 17:53:53.812372	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
853	54	✅ Successful login	2025-04-15 18:06:41.218832	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
854	54	✅ TOTP verified successfully	2025-04-15 18:06:53.561792	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
855	22	❌ Failed login: Invalid password (2)	2025-04-15 18:07:22.436671	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
856	22	✅ Successful login	2025-04-15 18:07:28.546241	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
857	22	✅ TOTP verified successfully	2025-04-15 18:07:46.488632	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
858	22	🔐 Logged in via WebAuthn (USB security key)	2025-04-15 18:07:51.717781	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
859	54	✅ Successful login	2025-04-15 18:37:46.579168	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
860	54	✅ TOTP verified successfully	2025-04-15 18:38:08.959126	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
861	54	🔐 Logged in via WebAuthn (USB security key)	2025-04-15 18:38:18.279377	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
862	57	❌ Failed login: Invalid password (2)	2025-04-15 18:38:36.480297	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
863	57	❌ Failed login: Invalid password (3)	2025-04-15 18:38:48.296409	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
864	57	✅ Successful login	2025-04-15 18:38:54.569422	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
865	57	✅ TOTP verified successfully	2025-04-15 18:39:06.406026	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
866	57	🔐 Logged in via WebAuthn (USB security key)	2025-04-15 18:39:47.537346	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
867	22	✅ Successful login	2025-04-15 18:40:04.681966	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
868	22	✅ TOTP verified successfully	2025-04-15 18:40:23.023861	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
869	22	🔐 Logged in via WebAuthn (USB security key)	2025-04-15 18:40:30.07397	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
870	54	✅ Successful login	2025-04-15 18:45:19.162787	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
871	54	✅ TOTP verified successfully	2025-04-15 18:45:37.976102	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
872	54	🔐 Logged in via WebAuthn (USB security key)	2025-04-15 18:45:43.329563	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
873	54	✅ Successful login	2025-04-15 18:45:57.303942	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
874	54	✅ TOTP verified successfully	2025-04-15 18:46:07.407237	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
875	\N	⚠️ Client-side WebAuthn failure: publicKey is not defined	2025-04-15 19:00:47.712415	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
876	22	✅ Successful login	2025-04-15 19:02:23.290154	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
877	22	✅ TOTP verified successfully	2025-04-15 19:02:41.539892	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
878	\N	⚠️ Client-side WebAuthn failure: publicKey is not defined	2025-04-15 19:02:42.120771	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
879	22	🔐 Logged in via WebAuthn (USB security key)	2025-04-15 19:02:46.611826	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
880	54	✅ Successful login	2025-04-15 19:08:02.396606	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
881	54	✅ TOTP verified successfully	2025-04-15 19:08:16.603112	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
882	54	⚠️ Client-side WebAuthn failure: publicKey is not defined	2025-04-15 19:08:17.185862	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
883	22	✅ Successful login	2025-04-15 19:09:03.708552	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
884	22	✅ TOTP verified successfully	2025-04-15 19:09:28.738635	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
885	22	⚠️ Client-side WebAuthn failure: publicKey is not defined	2025-04-15 19:09:29.315654	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
886	22	🔐 Logged in via WebAuthn (USB security key)	2025-04-15 19:09:35.8724	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
887	57	✅ Successful login	2025-04-15 19:10:54.624992	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
888	57	✅ TOTP verified successfully	2025-04-15 19:11:08.023326	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
889	57	⚠️ Client-side WebAuthn failure: publicKey is not defined	2025-04-15 19:11:08.596647	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
890	57	🔐 Logged in via WebAuthn (USB security key)	2025-04-15 19:11:14.345344	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
891	58	✅ Successful login	2025-04-15 19:13:41.694587	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
892	58	✅ TOTP verified successfully	2025-04-15 19:14:13.730763	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
893	58	✅ TOTP verified successfully	2025-04-15 19:15:21.213706	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
894	58	⚠️ Client-side WebAuthn failure: publicKey is not defined	2025-04-15 19:15:21.83336	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
895	58	🔐 Logged in via WebAuthn (cross-device passkey)	2025-04-15 19:15:39.974954	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
896	22	✅ Successful login	2025-04-16 08:52:31.743795	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
897	22	✅ TOTP verified successfully	2025-04-16 08:53:06.901572	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
898	22	⚠️ Client-side WebAuthn failure: publicKey is not defined	2025-04-16 08:53:07.507139	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
899	22	🔐 Logged in via WebAuthn (USB security key)	2025-04-16 08:53:53.888332	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
900	22	✅ Successful login	2025-04-16 09:02:15.230768	192.168.2.115	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
901	22	❌ Failed TOTP verification (1)	2025-04-16 09:02:31.734367	192.168.2.115	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
902	22	✅ TOTP verified successfully	2025-04-16 09:02:43.768505	192.168.2.115	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
903	22	⚠️ Client-side WebAuthn failure: Cannot read properties of undefined (reading 'get')	2025-04-16 09:02:44.315622	192.168.2.115	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
904	22	⚠️ Client-side WebAuthn failure: Cannot read properties of undefined (reading 'get')	2025-04-16 09:03:14.85712	192.168.2.115	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
905	22	✅ Successful login	2025-04-16 09:27:59.474122	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
906	22	✅ TOTP verified successfully	2025-04-16 09:28:14.650215	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
907	22	⚠️ Client-side WebAuthn failure: publicKey is not defined	2025-04-16 09:28:15.215914	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
908	22	🔐 Logged in via WebAuthn (USB security key)	2025-04-16 09:28:20.531918	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
909	57	✅ Successful login	2025-04-16 09:35:17.628223	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
910	57	✅ TOTP verified successfully	2025-04-16 09:35:37.665764	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
911	56	✅ Successful login	2025-04-16 09:36:14.991626	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
912	56	✅ TOTP verified successfully	2025-04-16 09:36:23.77783	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
913	54	✅ Successful login	2025-04-16 09:36:56.56002	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
914	54	✅ TOTP verified successfully	2025-04-16 09:37:10.409588	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
915	58	✅ Successful login	2025-04-16 09:37:42.806784	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
916	58	✅ TOTP verified successfully	2025-04-16 09:37:48.622196	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
917	58	🔐 Logged in via WebAuthn (cross-device passkey)	2025-04-16 09:40:27.057962	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
918	22	✅ Successful login	2025-04-16 09:40:55.030739	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
919	22	✅ TOTP verified successfully	2025-04-16 09:41:10.018611	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
920	22	🔐 Logged in via WebAuthn (USB security key)	2025-04-16 09:41:16.640611	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
921	57	✅ Successful login	2025-04-16 09:41:50.57237	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
922	57	❌ Failed TOTP verification (1)	2025-04-16 09:42:07.024774	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
923	57	✅ TOTP verified successfully	2025-04-16 09:42:17.848898	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
924	57	⚠️ Client-side WebAuthn failure: The operation either timed out or was not allowed. See: https://www.w3.org/TR/webauthn-2/#sctn-privacy-considerations-client.	2025-04-16 09:42:26.197745	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
925	22	❌ Failed login: Invalid password (1)	2025-04-16 09:42:47.806532	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
926	22	✅ Successful login	2025-04-16 09:42:54.101038	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
927	22	✅ TOTP verified successfully	2025-04-16 09:43:13.426814	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
928	22	🔐 Logged in via WebAuthn (USB security key)	2025-04-16 09:43:18.79819	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
929	57	✅ Successful login	2025-04-16 09:47:30.364613	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
930	57	✅ TOTP verified successfully	2025-04-16 09:47:42.121321	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
931	22	✅ Successful login	2025-04-16 09:48:17.233123	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
932	22	❌ Failed TOTP verification (2)	2025-04-16 09:48:32.599681	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
933	22	✅ TOTP verified successfully	2025-04-16 09:48:42.466765	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
934	22	🔐 Logged in via WebAuthn (USB security key)	2025-04-16 09:48:47.456798	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
935	22	✅ Successful login	2025-04-16 10:07:51.463655	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
936	22	✅ TOTP verified successfully	2025-04-16 10:08:07.318649	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
937	22	🔐 Logged in via WebAuthn (USB security key)	2025-04-16 10:08:12.015614	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
938	22	✅ Successful login	2025-04-16 10:40:10.214637	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
939	22	✅ TOTP verified successfully	2025-04-16 10:40:23.410743	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
940	22	🔐 Logged in via WebAuthn (USB security key)	2025-04-16 10:40:28.214919	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
941	22	✅ Successful login	2025-04-16 11:03:25.084198	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
942	22	❌ Failed TOTP verification (3)	2025-04-16 11:03:31.11754	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
943	22	✅ TOTP verified successfully	2025-04-16 11:03:42.437352	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
944	22	🔐 Logged in via WebAuthn (USB security key)	2025-04-16 11:03:46.666251	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
945	22	✅ Successful login	2025-04-16 11:19:18.747502	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
946	22	✅ TOTP verified successfully	2025-04-16 11:19:28.908633	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
947	22	🔐 Logged in via WebAuthn (USB security key)	2025-04-16 11:19:33.303651	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
948	54	✅ Successful login	2025-04-16 11:20:55.063647	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
949	54	✅ TOTP verified successfully	2025-04-16 11:21:08.002097	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
950	54	🔐 Logged in via WebAuthn (USB security key)	2025-04-16 11:21:12.997028	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
951	22	✅ Successful login	2025-04-16 11:35:27.25925	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
952	22	✅ TOTP verified successfully	2025-04-16 11:35:44.040448	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
953	22	🔐 Logged in via WebAuthn (USB security key)	2025-04-16 11:35:49.185493	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
954	22	✅ Successful login	2025-04-16 11:57:32.22612	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
955	22	✅ TOTP verified successfully	2025-04-16 11:57:39.810167	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
956	22	🔐 Logged in via WebAuthn (USB security key)	2025-04-16 11:57:45.227229	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
957	22	✅ Successful login	2025-04-16 14:52:18.812235	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
958	22	✅ TOTP verified successfully	2025-04-16 14:52:39.488961	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
959	22	🔐 Logged in via WebAuthn (USB security key)	2025-04-16 14:53:17.80879	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
960	54	✅ Successful login	2025-04-16 15:36:24.50025	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
961	54	✅ TOTP verified successfully	2025-04-16 15:36:39.759576	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
962	54	🔐 Logged in via WebAuthn (USB security key)	2025-04-16 15:36:45.117582	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
963	59	🆕 New user registered using ICCID 8901774409043052 (SIM created by: 54)	2025-04-16 15:40:08.236575	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
964	59	✅ Successful login	2025-04-16 15:40:33.301981	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
965	59	✅ Successful login	2025-04-16 15:46:20.89036	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
966	59	✅ Successful login	2025-04-16 15:47:20.873097	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
967	22	❌ Failed login: Invalid password (2)	2025-04-16 15:48:37.406382	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
968	22	❌ Failed login: Invalid password (3)	2025-04-16 15:48:43.844161	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
969	22	✅ Successful login	2025-04-16 15:48:50.633503	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
970	22	✅ TOTP verified successfully	2025-04-16 15:49:10.052423	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
971	22	🔐 Logged in via WebAuthn (USB security key)	2025-04-16 15:49:14.983998	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
972	22	✏️ Edited user Register ZTN (0785796308) — Fields updated: email	2025-04-16 15:50:28.393622	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Headquarters	f	1
973	59	✅ Successful login	2025-04-16 15:50:45.570741	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
974	59	❌ Failed TOTP verification (1)	2025-04-16 15:51:30.432431	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
975	59	✅ TOTP verified successfully	2025-04-16 15:51:39.757662	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
976	59	✅ TOTP verified successfully	2025-04-16 15:52:28.038691	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
977	59	🔐 Logged in via WebAuthn (USB security key)	2025-04-16 15:52:32.938158	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
978	22	✅ Successful login	2025-04-16 15:53:01.848906	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
979	22	✅ TOTP verified successfully	2025-04-16 15:53:14.098008	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
980	22	🔐 Logged in via WebAuthn (USB security key)	2025-04-16 15:53:18.438199	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
981	22	✅ Successful login	2025-04-16 16:58:53.510496	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
982	22	✅ TOTP verified successfully	2025-04-16 16:59:06.053089	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
983	22	🔐 Logged in via WebAuthn (USB security key)	2025-04-16 16:59:11.357505	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
984	22	✅ Successful login	2025-04-16 17:31:54.318898	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
985	22	✅ TOTP verified successfully	2025-04-16 17:32:13.326415	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
986	22	🔐 Logged in via WebAuthn (USB security key)	2025-04-16 17:32:17.874632	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
987	22	✅ Successful login	2025-04-16 18:05:14.372253	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
988	22	✅ TOTP verified successfully	2025-04-16 18:05:27.834633	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
989	22	🔐 Logged in via WebAuthn (USB security key)	2025-04-16 18:05:32.269285	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
990	22	✅ Successful login	2025-04-16 18:23:07.927681	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
991	22	✅ TOTP verified successfully	2025-04-16 18:23:23.122283	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
992	22	🔐 Logged in via WebAuthn (USB security key)	2025-04-16 18:23:27.818238	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
993	22	✅ Successful login	2025-04-16 18:42:06.084136	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
994	22	✅ TOTP verified successfully	2025-04-16 18:42:18.797123	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
995	22	🔐 Logged in via WebAuthn (USB security key)	2025-04-16 18:42:23.481108	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
996	22	✅ Successful login	2025-04-16 19:07:25.117874	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
997	22	✅ TOTP verified successfully	2025-04-16 19:08:37.263372	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
998	22	🔐 Logged in via WebAuthn (USB security key)	2025-04-16 19:08:41.798255	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
999	22	📱 Admin generated SIM: 8901966840503626 with mobile 0787804967	2025-04-16 19:13:19.720334	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Headquarters	f	1
1000	22	📱 Admin generated SIM: 8901393980322340 with mobile 0787390971	2025-04-16 19:15:27.677742	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Headquarters	f	1
1001	22	✅ Successful login	2025-04-16 19:32:13.657	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1002	22	✅ TOTP verified successfully	2025-04-16 19:32:39.4329	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1003	22	🔐 Logged in via WebAuthn (USB security key)	2025-04-16 19:32:44.057914	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1004	22	📱 Admin generated SIM: 8901872233826917 with mobile 0787344458	2025-04-16 19:34:02.674513	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Headquarters	f	1
1005	22	📱 Admin generated SIM: 8901326347934792 with mobile 0787569319	2025-04-16 19:47:07.773468	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Headquarters	f	1
1006	22	✅ Successful login	2025-04-16 19:48:09.960524	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1007	22	✅ TOTP verified successfully	2025-04-16 19:48:26.122304	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1008	22	🔐 Logged in via WebAuthn (USB security key)	2025-04-16 19:48:30.402764	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1009	54	✅ Successful login	2025-04-17 15:41:42.589008	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1010	54	❌ Failed TOTP verification (1)	2025-04-17 15:41:59.902538	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1011	54	✅ TOTP verified successfully	2025-04-17 15:42:09.326508	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1012	54	🔐 Logged in via WebAuthn (USB security key)	2025-04-17 15:43:20.135878	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1013	54	✅ Successful login	2025-04-17 15:58:21.470766	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1014	54	✅ TOTP verified successfully	2025-04-17 15:58:36.774011	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1015	54	🔐 Logged in via WebAuthn (USB security key)	2025-04-17 15:58:50.821496	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1016	60	🆕 New user registered using ICCID 8901403627430297 (SIM created by: 54)	2025-04-17 16:00:39.135322	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1017	60	✅ Successful login	2025-04-17 16:00:54.563441	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1018	60	✅ TOTP verified successfully	2025-04-17 16:01:23.534449	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1019	60	✅ TOTP verified successfully	2025-04-17 16:03:36.290788	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1020	60	🔐 Logged in via WebAuthn (cross-device passkey)	2025-04-17 16:05:06.941668	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1021	58	❌ Failed login: Invalid password (1)	2025-04-17 16:05:36.825478	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1022	58	❌ Failed login: Invalid password (2)	2025-04-17 16:05:39.584626	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1023	58	❌ Failed login: Invalid password (3)	2025-04-17 16:05:42.02635	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1028	54	✅ TOTP verified successfully	2025-04-17 16:10:15.44579	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
1030	57	❌ Failed TOTP verification (1)	2025-04-17 16:10:58.355068	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
1043	57	❌ Failed login: Invalid password (5)	2025-04-17 16:47:04.212631	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
1044	57	🚨 Account temporarily locked due to failed login attempts	2025-04-17 16:47:04.212631	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
1223	22	✅ Successful login	2025-04-23 16:24:25.195748	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1224	22	✅ TOTP verified successfully	2025-04-23 16:24:46.039498	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1225	22	🔐 Logged in via WebAuthn (USB security key)	2025-04-23 16:24:51.609345	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1226	58	✅ Successful login	2025-04-23 16:29:28.091945	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1242	56	📧 Password reset requested	2025-04-23 17:19:18.39166	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1243	56	❌ Tried reusing a previous password during reset	2025-04-23 17:20:44.463733	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1244	56	🔐 Password reset successful	2025-04-23 17:21:04.996273	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1264	54	📨 TOTP reset link requested	2025-04-24 09:56:24.917489	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1265	54	⚠️ TOTP reset denied due to low trust score	2025-04-24 09:57:54.459865	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1277	54	📨 TOTP reset link requested	2025-04-24 15:55:42.429222	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1286	54	📨 TOTP reset link requested	2025-04-24 16:54:30.948428	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1297	54	📨 TOTP reset link requested	2025-04-24 19:27:05.959507	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1298	54	✅ TOTP reset after identity + trust check	2025-04-24 19:27:52.260101	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1299	54	✅ Successful login	2025-04-24 19:28:46.427901	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1320	56	✅ TOTP verified successfully	2025-04-24 19:59:25.843725	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1323	56	✅ TOTP reset after identity + trust check	2025-04-24 20:05:55.407504	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1345	54	✅ Password reset after MFA and trust check	2025-04-25 10:08:00.005442	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1346	54	❌ Failed login: Invalid password (1)	2025-04-25 10:08:35.876953	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1347	54	✅ Successful login	2025-04-25 10:08:42.844272	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1362	54	✅ TOTP verified successfully	2025-04-25 10:39:38.924977	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1380	54	❌ Attempted to reuse an old password during reset	2025-04-25 11:49:25.970665	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1388	56	📨 WebAuthn reset link requested	2025-04-25 16:04:09.2019	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	t	1
1407	22	✅ Successful login	2025-04-25 17:23:17.095128	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1409	22	🔐 Logged in via WebAuthn (USB security key)	2025-04-25 17:24:18.655508	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1411	54	✅ Successful login	2025-04-25 17:25:09.966674	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1422	55	✅ TOTP verified successfully	2025-04-25 17:32:11.427522	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1426	22	🔐 Logged in via WebAuthn (USB security key)	2025-04-25 17:33:50.682952	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1431	54	❌ Attempted to reuse an old password during reset	2025-04-25 20:21:08.480138	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1432	54	✅ Password reset after MFA and checks	2025-04-25 20:22:49.546125	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1433	22	✅ Successful login	2025-04-25 20:25:19.053288	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1434	54	❌ Failed login: Invalid password (3)	2025-04-25 20:25:36.563292	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1435	54	✅ Successful login	2025-04-25 20:25:42.604126	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1436	54	✅ TOTP verified successfully	2025-04-25 20:26:11.240468	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1437	54	🔐 Logged in via WebAuthn (USB security key)	2025-04-25 20:26:20.601751	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1024	58	❌ Failed login: Invalid password (4)	2025-04-17 16:05:45.485927	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1031	57	❌ Failed TOTP verification (2)	2025-04-17 16:11:07.992938	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
1040	57	❌ Failed login: Invalid password (2)	2025-04-17 16:46:55.140006	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
1045	22	❌ Failed login: Invalid password (1)	2025-04-17 16:47:55.213324	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1227	58	✅ TOTP verified successfully	2025-04-23 16:29:44.486846	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1245	56	📧 Password reset requested	2025-04-23 17:34:38.475813	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1246	56	❌ Tried reusing a previous password during reset	2025-04-23 17:35:18.812155	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1266	54	📨 TOTP reset link requested	2025-04-24 10:59:13.031323	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1278	54	📨 TOTP reset link requested	2025-04-24 16:13:02.665961	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1287	54	📨 TOTP reset link requested	2025-04-24 17:12:39.766695	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1300	54	📨 TOTP reset link requested	2025-04-24 19:37:40.3183	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1325	56	✅ TOTP verified successfully	2025-04-24 20:07:08.798492	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1329	56	✅ Successful login	2025-04-24 20:09:49.394449	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1348	54	📧 Password reset requested	2025-04-25 10:16:53.893629	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1349	54	✅ Password reset after MFA verification	2025-04-25 10:18:10.717523	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1350	54	❌ Failed login: Invalid password (2)	2025-04-25 10:18:57.623864	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1351	54	✅ Successful login	2025-04-25 10:19:08.048506	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1352	54	📧 Password reset requested	2025-04-25 10:20:50.234688	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1353	54	✅ Successful login	2025-04-25 10:22:40.632774	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
1354	54	✅ TOTP verified successfully	2025-04-25 10:23:07.130155	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
1355	54	⚠️ Client-side WebAuthn failure: User cancelled or did not interact with WebAuthn prompt in time. (NotAllowedError: The request is not allowed by the user agent or the platform in the current context, possibly because the user denied permission.)	2025-04-25 10:23:25.589961	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
1356	54	🔐 Logged in via WebAuthn (USB security key)	2025-04-25 10:23:38.281808	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
1363	54	📧 Password reset requested	2025-04-25 10:54:45.179227	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1364	54	✅ Password reset after MFA verification	2025-04-25 10:56:54.601599	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1365	54	📧 Password reset requested	2025-04-25 10:57:10.966577	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1366	54	✅ Password reset after MFA verification	2025-04-25 10:57:48.914026	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1389	56	📨 WebAuthn reset link requested	2025-04-25 16:05:05.30223	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	t	1
1408	22	✅ TOTP verified successfully	2025-04-25 17:23:44.967929	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1410	22	🔓 Unlocked user account for Pathos Mut (0787832379)	2025-04-25 17:24:48.940202	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Admin Panel	f	1
1412	54	✅ TOTP verified successfully	2025-04-25 17:25:24.527719	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1414	54	📨 WebAuthn reset link requested	2025-04-25 17:25:57.068114	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1416	54	✅ Successful login	2025-04-25 17:27:35.13674	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1420	55	✅ Successful login	2025-04-25 17:31:37.048662	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1425	22	✅ TOTP verified successfully	2025-04-25 17:33:43.279636	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1427	22	📱 Admin generated SIM: 8901858579226525 with mobile 0787710926	2025-04-25 17:34:50.047384	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Headquarters	f	1
1438	62	🆕 New user registered using ICCID 8901871711562650 (SIM created by: 54)	2025-04-25 20:34:51.594357	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1440	62	✅ TOTP verified successfully	2025-04-25 20:35:51.597453	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1442	54	✅ Successful login	2025-04-25 20:42:57.675706	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1025	58	❌ Failed login: Invalid password (5)	2025-04-17 16:05:46.904378	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1026	58	🚨 Account temporarily locked due to failed login attempts	2025-04-17 16:05:46.904378	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1032	22	✅ Successful login	2025-04-17 16:12:22.796751	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1039	57	❌ Failed login: Invalid password (1)	2025-04-17 16:46:51.479481	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
1050	22	🔓 Unlocked user account for Bio test (0787408913)	2025-04-17 17:00:38.981219	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Admin Panel	f	1
1228	58	🔐 Logged in via WebAuthn (USB security key)	2025-04-23 16:30:32.305077	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1229	58	✅ Successful login	2025-04-23 16:32:06.374441	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1231	58	⚠️ Client-side WebAuthn failure: User cancelled or did not interact with WebAuthn prompt in time. (NotAllowedError: The operation either timed out or was not allowed. See: https://www.w3.org/TR/webauthn-2/#sctn-privacy-considerations-client.)	2025-04-23 16:32:20.425235	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1247	56	🚫 Password reset denied due to low trust score	2025-04-23 17:36:23.513315	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1267	54	📨 TOTP reset link requested	2025-04-24 11:23:50.952801	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1279	54	📨 TOTP reset link requested	2025-04-24 16:28:56.29906	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1280	54	✅ Successful login	2025-04-24 16:30:01.7226	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1281	54	✅ TOTP verified successfully	2025-04-24 16:30:17.118417	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1282	54	🔐 Logged in via WebAuthn (USB security key)	2025-04-24 16:30:30.550577	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1284	22	✅ TOTP verified successfully	2025-04-24 16:35:57.000053	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1285	22	🔐 Logged in via WebAuthn (USB security key)	2025-04-24 16:36:04.550466	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1288	54	📨 TOTP reset link requested	2025-04-24 17:31:19.524635	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1301	54	✅ TOTP reset after identity + trust check	2025-04-24 19:40:13.656619	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1302	56	📨 TOTP reset link requested	2025-04-24 19:40:43.574005	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1303	56	✅ TOTP reset after identity + trust check	2025-04-24 19:41:20.192396	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1304	56	✅ Successful login	2025-04-24 19:42:45.863443	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1305	54	❌ Failed login: Invalid password (2)	2025-04-24 19:48:07.722119	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1306	54	✅ Successful login	2025-04-24 19:48:14.711245	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1307	54	✅ Successful login	2025-04-24 19:52:59.537852	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1331	56	🔐 Logged in via WebAuthn (USB security key)	2025-04-24 20:10:32.518565	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1357	54	🔁 WebAuthn reset requested by user	2025-04-25 10:24:19.682684	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
1367	54	📧 Password reset requested	2025-04-25 11:01:46.829143	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1368	54	✅ Password reset after MFA verification	2025-04-25 11:02:39.077527	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1390	54	✅ Successful login	2025-04-25 16:19:52.105232	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1391	54	✅ TOTP verified successfully	2025-04-25 16:20:13.957979	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1392	54	⚠️ Client-side WebAuthn failure: User cancelled or did not interact with WebAuthn prompt in time. (NotAllowedError: The operation either timed out or was not allowed. See: https://www.w3.org/TR/webauthn-2/#sctn-privacy-considerations-client.)	2025-04-25 16:20:17.748805	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1393	54	📨 WebAuthn reset link requested	2025-04-25 16:20:40.49828	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1413	54	⚠️ Client-side WebAuthn failure: User cancelled or did not interact with WebAuthn prompt in time. (NotAllowedError: The operation either timed out or was not allowed. See: https://www.w3.org/TR/webauthn-2/#sctn-privacy-considerations-client.)	2025-04-25 17:25:30.712453	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1415	54	✅ WebAuthn reset verified	2025-04-25 17:26:44.604966	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1419	54	🧾 Agent deposited 7839.0 RWF to Dary (0782409658)	2025-04-25 17:30:26.117542	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	34.7315, 135.7347	f	1
1439	62	✅ Successful login	2025-04-25 20:35:14.576028	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1027	54	✅ Successful login	2025-04-17 16:09:47.687975	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
1029	57	✅ Successful login	2025-04-17 16:10:43.03642	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	f	1
1034	22	✅ TOTP verified successfully	2025-04-17 16:13:47.82546	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1037	22	✅ TOTP verified successfully	2025-04-17 16:44:43.439415	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1042	57	❌ Failed login: Invalid password (4)	2025-04-17 16:47:01.994128	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
1047	22	✅ TOTP verified successfully	2025-04-17 16:48:14.546764	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1230	58	✅ TOTP verified successfully	2025-04-23 16:32:17.759332	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1248	56	❌ Tried reusing a previous password during reset	2025-04-23 17:36:55.547698	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1249	56	❌ Tried reusing a previous password during reset	2025-04-23 17:37:10.519215	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1250	56	❌ Tried reusing a previous password during reset	2025-04-23 17:37:22.705503	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1251	56	🔐 Password reset successful	2025-04-23 17:37:35.822495	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1268	54	📨 TOTP reset link requested	2025-04-24 11:39:28.010095	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1283	22	✅ Successful login	2025-04-24 16:35:35.086189	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1289	54	📨 TOTP reset link requested	2025-04-24 17:47:20.013063	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1308	54	❌ Failed TOTP verification (1)	2025-04-24 19:54:12.11439	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1309	54	📨 TOTP reset link requested	2025-04-24 19:54:25.607231	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1310	54	⚠️ TOTP reset denied due to low trust score	2025-04-24 19:54:49.743215	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1332	54	📧 Password reset requested	2025-04-24 21:00:53.075529	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1338	54	📧 Password reset requested	2025-04-25 09:05:02.678228	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1358	54	📧 Password reset requested	2025-04-25 10:37:25.903413	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1360	54	❌ Failed login: Invalid password (3)	2025-04-25 10:39:09.208782	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1369	54	📧 Password reset requested	2025-04-25 11:14:22.188765	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1370	54	📧 Password reset requested	2025-04-25 11:35:53.334169	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1371	54	✅ Password reset after MFA and checks	2025-04-25 11:38:09.374347	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1372	54	📧 Password reset requested	2025-04-25 11:39:05.671015	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1373	54	❌ Attempted to reuse an old password during reset	2025-04-25 11:39:31.133936	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1374	54	❌ Failed login: Invalid password (4)	2025-04-25 11:40:10.755292	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1375	54	✅ Successful login	2025-04-25 11:40:17.260773	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1376	54	✅ TOTP verified successfully	2025-04-25 11:40:39.974747	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1377	54	🔐 Logged in via WebAuthn (USB security key)	2025-04-25 11:41:04.28579	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1381	56	❌ Failed login: Invalid password (1)	2025-04-25 15:50:17.711315	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1382	56	❌ Failed login: Invalid password (2)	2025-04-25 15:50:21.889155	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1383	54	✅ Successful login	2025-04-25 15:50:46.318455	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1384	54	✅ TOTP verified successfully	2025-04-25 15:51:06.668466	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1394	54	📨 WebAuthn reset link requested	2025-04-25 16:38:43.840646	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1395	54	📨 WebAuthn reset link requested	2025-04-25 17:01:11.865054	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1418	54	🔐 Logged in via WebAuthn (USB security key)	2025-04-25 17:28:14.427337	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1423	55	🔐 Logged in via WebAuthn (USB security key)	2025-04-25 17:32:34.278888	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1033	22	❌ Failed TOTP verification (1)	2025-04-17 16:13:35.7544	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1035	22	🔐 Logged in via WebAuthn (USB security key)	2025-04-17 16:14:04.735678	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1036	22	✅ Successful login	2025-04-17 16:44:27.924176	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1038	22	🔐 Logged in via WebAuthn (USB security key)	2025-04-17 16:44:50.807727	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1041	57	❌ Failed login: Invalid password (3)	2025-04-17 16:46:59.695124	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	Unknown	t	1
1046	22	✅ Successful login	2025-04-17 16:48:00.558092	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1048	22	🔐 Logged in via WebAuthn (USB security key)	2025-04-17 16:48:22.683737	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1049	22	📱 Admin generated SIM: 8901421439883836 with mobile 0787178968	2025-04-17 16:50:55.392005	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Headquarters	f	1
1051	22	✅ Successful login	2025-04-18 14:14:28.385059	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1052	22	✅ TOTP verified successfully	2025-04-18 14:14:42.532758	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1053	22	🔐 Logged in via WebAuthn (USB security key)	2025-04-18 14:15:14.448448	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1054	22	✅ Successful login	2025-04-21 10:08:23.919486	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1055	22	✅ TOTP verified successfully	2025-04-21 10:08:57.08313	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1056	22	🔐 Logged in via WebAuthn (USB security key)	2025-04-21 10:09:56.385929	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1057	56	📧 Password reset requested	2025-04-21 11:41:00.170209	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
1058	56	📧 Password reset requested	2025-04-21 11:42:04.256027	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
1059	56	📧 Password reset requested	2025-04-21 11:43:59.813972	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
1060	56	📧 Password reset requested	2025-04-21 11:47:38.814742	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
1061	56	📧 Password reset requested	2025-04-21 12:00:10.822087	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1062	56	🔐 Password reset successful	2025-04-21 12:03:34.179654	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1063	56	📧 Password reset requested	2025-04-21 12:05:28.301452	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1064	56	🔐 Password reset successful	2025-04-21 12:05:54.64451	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1065	56	📧 Password reset requested	2025-04-21 16:05:58.378987	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1066	57	✅ Successful login	2025-04-21 16:07:59.077434	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1067	57	✅ TOTP verified successfully	2025-04-21 16:08:18.053806	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1068	57	🔐 Logged in via WebAuthn (USB security key)	2025-04-21 16:08:50.352336	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1069	56	❌ Failed login: Invalid password (1)	2025-04-21 16:23:50.130286	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1070	56	❌ Failed login: Invalid password (2)	2025-04-21 16:23:57.005111	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1071	56	✅ Successful login	2025-04-21 16:24:02.846873	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1072	56	✅ TOTP verified successfully	2025-04-21 16:24:20.738599	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1073	56	🔐 Logged in via WebAuthn (cross-device passkey)	2025-04-21 16:24:26.406558	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1074	56	✅ Successful login	2025-04-21 16:51:09.454908	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1075	56	✅ TOTP verified successfully	2025-04-21 16:51:25.408369	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1076	56	🔐 Logged in via WebAuthn (cross-device passkey)	2025-04-21 16:51:30.232105	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1077	58	✅ Successful login	2025-04-21 17:26:32.330929	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1078	58	❌ Failed TOTP verification (1)	2025-04-21 17:26:45.272915	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1079	58	❌ Failed TOTP verification (2)	2025-04-21 17:26:56.09915	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1080	56	✅ Successful login	2025-04-21 17:27:17.740047	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1081	56	❌ Failed TOTP verification (1)	2025-04-21 17:27:29.509978	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1082	56	✅ TOTP verified successfully	2025-04-21 17:27:43.509409	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1083	56	🔐 Logged in via WebAuthn (cross-device passkey)	2025-04-21 17:27:47.482812	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1084	56	✅ Successful login	2025-04-21 17:47:52.213816	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1085	56	✅ TOTP verified successfully	2025-04-21 17:48:08.120168	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1086	56	🔐 Logged in via WebAuthn (cross-device passkey)	2025-04-21 17:48:12.533889	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1087	56	✅ Successful login	2025-04-21 18:14:52.431903	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1088	56	✅ TOTP verified successfully	2025-04-21 18:15:11.584654	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1089	56	🔐 Logged in via WebAuthn (cross-device passkey)	2025-04-21 18:15:15.23071	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1090	56	✅ Successful login	2025-04-21 18:31:23.534891	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1091	56	❌ Failed TOTP verification (2)	2025-04-21 18:31:38.605932	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1092	56	✅ TOTP verified successfully	2025-04-21 18:32:08.343529	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1093	56	🔐 Logged in via WebAuthn (cross-device passkey)	2025-04-21 18:32:12.466387	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1094	56	✅ Successful login	2025-04-21 18:46:45.504169	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1095	56	✅ TOTP verified successfully	2025-04-21 18:47:06.473968	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1096	56	🔐 Logged in via WebAuthn (cross-device passkey)	2025-04-21 18:47:09.992679	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1097	56	✅ Successful login	2025-04-21 19:06:10.003258	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1098	56	✅ TOTP verified successfully	2025-04-21 19:06:23.025895	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1099	56	🔐 Logged in via WebAuthn (cross-device passkey)	2025-04-21 19:06:26.657344	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1100	56	❌ Failed TOTP verification (3)	2025-04-21 19:13:57.50599	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1101	56	✅ TOTP verified successfully	2025-04-21 19:14:09.022262	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1102	56	🔐 Logged in via WebAuthn (cross-device passkey)	2025-04-21 19:14:12.596716	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1103	56	✅ Successful login	2025-04-21 19:20:28.240832	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1104	56	✅ TOTP verified successfully	2025-04-21 19:20:40.577389	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1105	56	🔐 Logged in via WebAuthn (cross-device passkey)	2025-04-21 19:20:43.333612	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1106	56	✅ TOTP verified successfully	2025-04-21 19:34:37.51886	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1107	56	🔐 Logged in via WebAuthn (cross-device passkey)	2025-04-21 19:34:40.772891	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1108	56	❌ Failed login: Invalid password (3)	2025-04-21 19:35:58.498695	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1109	56	✅ Successful login	2025-04-21 19:36:04.414992	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1110	56	✅ TOTP verified successfully	2025-04-21 19:36:21.338945	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1111	56	🔐 Logged in via WebAuthn (cross-device passkey)	2025-04-21 19:36:24.677762	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1112	56	✅ Successful login	2025-04-21 19:59:36.047684	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1113	56	✅ TOTP verified successfully	2025-04-21 19:59:49.507277	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1114	56	🔐 Logged in via WebAuthn (cross-device passkey)	2025-04-21 19:59:53.623312	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1115	56	🔐 Changed account password	2025-04-21 20:04:22.009596	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	t	1
1116	56	❌ Failed login: Invalid password (4)	2025-04-21 20:22:06.527613	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1117	56	✅ Successful login	2025-04-21 20:22:10.703202	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1118	56	✅ TOTP verified successfully	2025-04-21 20:22:28.981862	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1119	56	🔐 Logged in via WebAuthn (cross-device passkey)	2025-04-21 20:22:32.916822	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1120	56	🔐 Changed account password	2025-04-21 20:24:41.919931	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1121	56	❌ Attempted to reuse an old password	2025-04-21 20:25:01.549526	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1122	56	❌ Attempted to reuse an old password	2025-04-21 20:25:09.833598	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1123	56	❌ Attempted to reuse an old password	2025-04-21 20:25:35.130684	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1124	56	🔐 Changed account password	2025-04-21 20:25:50.747729	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1125	56	✅ Successful login	2025-04-21 20:38:51.61791	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
1126	56	✅ TOTP verified successfully	2025-04-21 20:39:10.798074	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
1127	56	🔐 Logged in via WebAuthn (cross-device passkey)	2025-04-21 20:39:14.818219	127.0.0.1	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	Unknown	f	1
1128	56	🔁 TOTP reset requested by user	2025-04-21 20:42:26.660769	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1129	56	❌ Failed login: Invalid password (5)	2025-04-21 20:44:03.392155	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1130	56	🚨 Account temporarily locked due to failed login attempts	2025-04-21 20:44:03.392155	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1131	22	✅ Successful login	2025-04-21 20:45:42.106085	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1132	22	✅ TOTP verified successfully	2025-04-21 20:46:07.193373	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1133	22	🔐 Logged in via WebAuthn (USB security key)	2025-04-21 20:46:12.829917	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1134	22	🔓 Unlocked user account for Gabriel Darwin (SWP_1744070543)	2025-04-21 20:47:47.653332	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Admin Panel	f	1
1135	60	✅ Successful login	2025-04-21 20:48:19.801293	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1136	60	✅ TOTP verified successfully	2025-04-21 20:48:41.516533	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1137	60	🔐 Logged in via WebAuthn (cross-device passkey)	2025-04-21 20:49:02.204561	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1138	56	✅ Successful login	2025-04-21 20:50:27.708143	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1139	56	✅ TOTP verified successfully	2025-04-21 20:52:49.995325	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1140	56	🔐 Logged in via WebAuthn (cross-device passkey)	2025-04-21 20:52:53.611023	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1141	56	✅ Successful login	2025-04-21 21:27:01.666964	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1142	56	✅ TOTP verified successfully	2025-04-21 21:27:25.903021	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1143	56	🔐 Logged in via WebAuthn (cross-device passkey)	2025-04-21 21:27:30.106646	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1144	56	🔁 WebAuthn reset requested by user	2025-04-21 21:29:28.81672	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1145	56	✅ Successful login	2025-04-21 21:30:35.396395	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1146	56	✅ TOTP verified successfully	2025-04-21 21:31:09.900456	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1147	56	❌ Failed TOTP verification (4)	2025-04-21 21:32:14.20648	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1148	56	✅ TOTP verified successfully	2025-04-21 21:32:38.266129	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1149	56	🔐 Logged in via WebAuthn (cross-device passkey)	2025-04-21 21:32:53.873357	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1150	56	📧 Password reset requested	2025-04-21 21:42:05.113149	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1151	56	📧 Password reset requested	2025-04-21 21:50:51.798184	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1152	56	❌ Tried reusing a previous password during reset	2025-04-21 22:00:52.69049	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1153	56	❌ Tried reusing a previous password during reset	2025-04-21 22:01:29.478074	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1154	56	🔐 Password reset successful	2025-04-21 22:02:18.265445	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1155	56	📧 Password reset requested	2025-04-21 22:08:33.284153	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1156	56	❌ Tried reusing a previous password during reset	2025-04-21 22:12:57.430423	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1157	56	❌ Tried reusing a previous password during reset	2025-04-21 22:13:14.015447	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1158	56	🔐 Password reset successful	2025-04-21 22:13:43.54286	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1159	54	✅ Successful login	2025-04-21 22:14:55.906258	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1160	54	✅ TOTP verified successfully	2025-04-21 22:15:14.297238	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1161	54	🔐 Logged in via WebAuthn (USB security key)	2025-04-21 22:15:37.177807	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1162	56	✅ Successful login	2025-04-21 22:34:21.534179	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1163	56	✅ Successful login	2025-04-21 23:14:25.981383	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1164	56	❌ Failed login: Invalid password (6)	2025-04-21 23:15:41.910369	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1165	56	🚨 Account temporarily locked due to failed login attempts	2025-04-21 23:15:41.910369	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1166	56	✅ Successful login	2025-04-22 09:13:06.499898	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1167	56	✅ Successful login	2025-04-22 09:15:31.559744	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1168	56	❌ Failed TOTP verification (1)	2025-04-22 09:17:13.135867	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1169	56	✅ TOTP verified successfully	2025-04-22 09:17:43.274336	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1170	56	🔐 Logged in via WebAuthn (cross-device passkey)	2025-04-22 09:17:59.765589	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1171	56	✅ Successful login	2025-04-22 10:11:04.466831	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1172	56	✅ TOTP verified successfully	2025-04-22 10:11:19.605215	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1173	56	🔐 Logged in via WebAuthn (cross-device passkey)	2025-04-22 10:11:38.948295	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1174	54	✅ Successful login	2025-04-22 10:12:31.472758	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1175	54	✅ TOTP verified successfully	2025-04-22 10:12:49.290851	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1176	54	🔐 Logged in via WebAuthn (USB security key)	2025-04-22 10:13:11.085534	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1177	61	🆕 New user registered using ICCID 8901313847556763 (SIM created by: 54)	2025-04-22 10:19:10.615758	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1178	61	✅ Successful login	2025-04-22 10:19:58.828236	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1179	61	✅ TOTP verified successfully	2025-04-22 10:21:05.978566	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1180	61	✅ Successful login	2025-04-22 10:24:13.821281	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1181	61	✅ TOTP verified successfully	2025-04-22 10:25:17.599798	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1182	61	🔐 Logged in via WebAuthn (USB security key)	2025-04-22 10:25:22.850756	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1183	56	✅ Successful login	2025-04-22 10:55:00.869562	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1184	22	✅ Successful login	2025-04-22 11:11:10.746101	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1185	22	❌ Failed TOTP verification (1)	2025-04-22 11:13:53.720155	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1186	56	📨 TOTP reset link requested	2025-04-22 11:38:25.048857	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1187	56	📨 TOTP reset link requested	2025-04-22 11:44:10.32065	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1188	56	📨 TOTP reset link requested	2025-04-22 11:46:19.615983	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1189	56	📨 TOTP reset link requested	2025-04-22 11:56:23.603278	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1190	56	⚠️ TOTP reset denied due to low trust score	2025-04-22 11:58:45.89001	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1191	56	⚠️ TOTP reset denied due to low trust score	2025-04-22 11:59:15.501077	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1192	56	📨 TOTP reset link requested	2025-04-22 15:02:04.944698	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1193	56	⚠️ TOTP reset denied due to low trust score	2025-04-22 15:03:48.93486	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1194	56	⚠️ TOTP reset denied due to low trust score	2025-04-22 15:03:56.699249	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1195	56	⚠️ TOTP reset denied due to low trust score	2025-04-22 15:05:04.283452	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1196	56	📨 TOTP reset link requested	2025-04-22 15:21:26.049367	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1197	56	📨 TOTP reset link requested	2025-04-22 15:37:38.345349	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1198	56	📨 TOTP reset link requested	2025-04-22 15:58:06.868939	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1199	56	❌ Failed login: Invalid password (1)	2025-04-22 16:00:20.193327	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1200	56	✅ Successful login	2025-04-22 16:00:26.029025	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1201	56	✅ TOTP verified successfully	2025-04-22 16:00:41.27222	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1202	56	🔐 Logged in via WebAuthn (cross-device passkey)	2025-04-22 16:00:57.686391	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1203	56	✅ Successful login	2025-04-22 16:29:51.49097	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1204	56	✅ TOTP verified successfully	2025-04-22 16:30:21.761669	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1205	56	📨 TOTP reset link requested	2025-04-22 16:30:45.113251	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1206	56	📨 TOTP reset link requested	2025-04-22 16:46:46.579418	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1207	22	✅ Successful login	2025-04-22 16:58:08.837819	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1208	22	✅ TOTP verified successfully	2025-04-22 16:58:26.961332	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1209	56	❌ Failed login: Invalid password (1)	2025-04-23 09:20:37.651581	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1210	56	✅ Successful login	2025-04-23 09:20:43.944589	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1211	56	❌ Failed login: Invalid password (2)	2025-04-23 15:18:52.620471	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1212	54	✅ Successful login	2025-04-23 15:19:05.980014	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1213	54	✅ TOTP verified successfully	2025-04-23 15:19:23.10439	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1214	22	✅ Successful login	2025-04-23 15:44:33.031405	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1215	22	✅ TOTP verified successfully	2025-04-23 15:44:56.714402	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1216	22	🔐 Logged in via WebAuthn (USB security key)	2025-04-23 15:45:09.335491	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1217	57	✅ Successful login	2025-04-23 15:46:22.643183	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1218	57	❌ Failed TOTP verification (1)	2025-04-23 15:46:41.514672	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1232	56	📧 Password reset requested	2025-04-23 16:57:10.500351	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1233	56	🚫 Password reset denied due to low trust score	2025-04-23 16:58:15.814243	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1252	56	📧 Password reset requested	2025-04-23 17:48:35.972539	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1253	56	❌ Tried reusing a previous password during reset	2025-04-23 17:49:10.053585	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1254	56	🔐 Password reset successful	2025-04-23 17:50:03.205524	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1269	54	📨 TOTP reset link requested	2025-04-24 11:58:53.875738	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1290	54	📨 TOTP reset link requested	2025-04-24 18:06:21.622448	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1311	54	✅ TOTP reset after identity + trust check	2025-04-24 19:55:31.132796	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1312	54	✅ Successful login	2025-04-24 19:55:50.957892	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1313	54	✅ TOTP verified successfully	2025-04-24 19:56:40.828273	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1314	54	🔐 Logged in via WebAuthn (USB security key)	2025-04-24 19:56:46.906895	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1315	56	✅ Successful login	2025-04-24 19:57:22.508261	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1318	56	✅ TOTP reset after identity + trust check	2025-04-24 19:58:18.507754	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1321	56	🔐 Logged in via WebAuthn (USB security key)	2025-04-24 20:00:05.920661	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1324	56	✅ Successful login	2025-04-24 20:06:21.120936	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1443	54	✅ TOTP verified successfully	2025-04-25 20:43:13.157862	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1446	54	✅ Successful login	2025-04-25 21:00:30.80121	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1448	54	🔐 Logged in via WebAuthn (USB security key)	2025-04-25 21:00:56.650782	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1444	54	🔐 Logged in via WebAuthn (USB security key)	2025-04-25 20:43:18.052028	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
1445	54	❌ Failed login: Invalid password (3)	2025-04-25 21:00:20.970696	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	t	1
1447	54	✅ TOTP verified successfully	2025-04-25 21:00:48.864554	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	Unknown	f	1
\.


--
-- Data for Name: sim_cards; Type: TABLE DATA; Schema: public; Owner: ztn
--

COPY public.sim_cards (id, iccid, mobile_number, network_provider, status, registered_by, registration_date, user_id) FROM stdin;
4	8901195611744289	0788771617	MTN Rwanda	active	System	2025-03-11 10:47:53.223841	22
5	8901107192952337	0787524422	MTN Rwanda	unregistered	Admin	2025-03-11 12:44:35.63852	\N
6	8901585686962256	0787465095	MTN Rwanda	unregistered	Admin	2025-03-11 12:44:41.668041	\N
7	8901592508993020	0787236466	MTN Rwanda	unregistered	Admin	2025-03-11 12:45:20.184161	\N
8	8901272923494847	0787985202	MTN Rwanda	unregistered	Admin	2025-03-11 12:48:24.012481	\N
9	8901328904991250	0787266471	MTN Rwanda	unregistered	Admin	2025-03-11 12:55:24.307426	\N
10	8901435892611062	0787396738	MTN Rwanda	unregistered	Admin	2025-03-11 12:55:35.403458	\N
11	8901744337260655	0787227678	MTN Rwanda	unregistered	Admin	2025-03-11 12:55:43.395047	\N
12	8901530400422917	0787129547	MTN Rwanda	unregistered	Admin	2025-03-11 12:57:11.929775	\N
13	8901750761255889	0787294215	MTN Rwanda	unregistered	Admin	2025-03-11 14:21:01.690728	\N
15	8901947390996099	0787874891	MTN Rwanda	unregistered	Admin	2025-03-11 14:45:18.545366	\N
16	8901599867013139	0787471501	MTN Rwanda	unregistered	Admin	2025-03-11 14:45:51.953292	\N
17	8901955017786146	0787321768	MTN Rwanda	unregistered	Admin	2025-03-12 01:26:57.528209	\N
18	8901230465145905	0787226686	MTN Rwanda	unregistered	Admin	2025-03-12 01:27:21.1596	\N
14	8901480983689688	0787429600	MTN Rwanda	active	Admin	2025-03-11 14:21:36.525814	\N
19	8901900773433520	0787987447	MTN Rwanda	unregistered	Admin	2025-03-12 01:58:51.369496	\N
21	8901350947749959	0787617972	MTN Rwanda	unregistered	Admin	2025-03-12 02:05:08.70573	\N
23	8901616956735347	0787198750	MTN Rwanda	unregistered	Admin	2025-03-12 02:45:38.585316	\N
67	8901969372304026	0787265142	MTN	suspended	39	2025-03-13 01:52:18.747351	\N
25	8901734437844326	0787227314	MTN Rwanda	unregistered	Admin	2025-03-12 02:55:31.251253	\N
65	8901342372760031	0787805876	MTN	active	39	2025-03-13 01:51:20.802783	\N
27	8901727357155789	0787809572	MTN Rwanda	unregistered	Admin	2025-03-12 06:17:48.672192	\N
28	8901108815695271	0787549405	MTN Rwanda	unregistered	Admin	2025-03-12 06:18:04.10037	\N
29	8901115196661032	0787466853	MTN Rwanda	unregistered	Admin	2025-03-12 06:18:06.739829	\N
30	8901913586189207	0787931889	MTN Rwanda	unregistered	Admin	2025-03-12 06:24:35.059213	\N
31	8901902021266326	0787421383	MTN Rwanda	unregistered	Admin	2025-03-12 06:24:48.813437	\N
32	8901426119815573	0787723327	MTN Rwanda	unregistered	Admin	2025-03-12 06:24:49.982135	\N
33	8901383813872447	0787944501	MTN Rwanda	unregistered	Admin	2025-03-12 06:24:50.922521	\N
34	8901710279218908	0787247511	MTN Rwanda	unregistered	Admin	2025-03-12 06:24:52.973595	\N
35	8901775140136208	0787840941	MTN Rwanda	unregistered	Admin	2025-03-12 06:24:54.147071	\N
36	8901252248449839	0787898245	MTN Rwanda	unregistered	Admin	2025-03-12 06:24:55.151956	\N
37	8901227360945065	0787842298	MTN Rwanda	unregistered	Admin	2025-03-12 06:24:57.273446	\N
38	8901842341760350	0787433014	MTN Rwanda	unregistered	Admin	2025-03-12 06:28:57.303062	\N
39	8901549741128882	0787969036	MTN Rwanda	unregistered	Admin	2025-03-12 06:29:10.204465	\N
40	8901603548971999	0787752065	MTN Rwanda	unregistered	Admin	2025-03-12 06:29:35.185992	\N
41	8901200398014537	0787340733	MTN Rwanda	unregistered	Admin	2025-03-12 06:30:49.617883	\N
42	8901113118820478	0787391023	MTN Rwanda	unregistered	Admin	2025-03-12 06:30:54.262734	\N
43	8901935632497107	0787347054	MTN Rwanda	unregistered	Admin	2025-03-12 06:36:45.534267	\N
44	8901179680068581	0787910707	MTN Rwanda	unregistered	Admin	2025-03-12 06:37:25.735542	\N
45	8901466707925712	0787318407	MTN Rwanda	unregistered	Admin	2025-03-12 06:38:04.161881	\N
46	8901834154591742	0787931566	MTN Rwanda	unregistered	Admin	2025-03-12 06:44:47.78515	\N
47	8901919308296993	0787907977	MTN Rwanda	unregistered	Admin	2025-03-12 06:44:53.866805	\N
48	8901915165209024	0787456372	MTN Rwanda	unregistered	Admin	2025-03-12 06:45:02.866328	\N
49	8901533552828217	0787528368	MTN Rwanda	unregistered	Admin	2025-03-12 06:45:10.780435	\N
50	8901832093500313	0787449329	MTN Rwanda	unregistered	Admin	2025-03-12 06:45:55.071246	\N
51	8901399274700797	0787503176	MTN Rwanda	unregistered	Admin	2025-03-12 06:47:45.148741	\N
52	8901653523147097	0787971466	MTN Rwanda	unregistered	Admin	2025-03-12 06:47:51.456821	\N
53	8901639351051880	0787512354	MTN Rwanda	unregistered	Admin	2025-03-12 06:50:38.02588	\N
54	8901265489773999	0787225521	MTN Rwanda	unregistered	Admin	2025-03-12 06:50:45.010351	\N
55	8901888715881070	0787474282	MTN Rwanda	unregistered	Admin	2025-03-12 06:50:59.127311	\N
56	8901377444431580	0787186874	MTN Rwanda	unregistered	Admin	2025-03-12 06:53:47.866157	\N
57	8901619932768581	0787713800	MTN Rwanda	unregistered	Admin	2025-03-12 06:55:22.502682	\N
58	8901650269709122	0787641231	MTN Rwanda	unregistered	Admin	2025-03-12 06:56:55.559552	\N
59	8901906257517253	0787962369	MTN Rwanda	unregistered	Admin	2025-03-12 06:57:27.933167	\N
60	8901237535846967	0787499728	MTN Rwanda	unregistered	Admin	2025-03-12 06:58:06.938253	\N
61	8901821749485286	0787388884	MTN Rwanda	unregistered	Admin	2025-03-12 06:58:33.597727	\N
75	8901886542637566	0787760887	MTN Rwanda	unregistered	Admin	2025-03-13 10:10:34.548729	\N
76	8901888932526698	0787825122	MTN Rwanda	unregistered	Admin	2025-03-13 10:51:44.923227	\N
77	8901411028324531	0787825674	MTN Rwanda	unregistered	Admin	2025-03-13 11:06:26.723368	\N
78	8901623034642645	0787672852	MTN Rwanda	unregistered	Admin	2025-03-13 11:06:30.649129	\N
79	8901465166466459	0787272337	MTN Rwanda	unregistered	Admin	2025-03-13 11:33:23.799807	\N
80	8901535278150059	0787695182	MTN Rwanda	unregistered	Admin	2025-03-13 11:33:26.08078	\N
82	8901883072017788	0787962319	MTN Rwanda	unregistered	Admin	2025-03-13 12:24:46.784802	\N
83	8901644343616606	0787555603	MTN Rwanda	unregistered	Admin	2025-03-13 13:25:43.548127	\N
84	8901848905540395	0787476279	MTN Rwanda	unregistered	Admin	2025-03-13 13:25:45.910108	\N
85	8901495419828237	0787333801	MTN Rwanda	unregistered	Admin	2025-03-13 14:26:21.322871	\N
86	8901268551062945	0787865687	MTN Rwanda	unregistered	Admin	2025-03-13 14:26:23.796535	\N
87	8901864168564032	0787894343	MTN Rwanda	unregistered	Admin	2025-03-13 14:42:10.463389	\N
88	8901672393699903	0787472404	MTN Rwanda	unregistered	Admin	2025-03-13 23:50:47.708873	\N
89	8901377833469245	0787868444	MTN Rwanda	unregistered	Admin	2025-03-14 02:16:33.424128	\N
90	8901729363062406	0787547559	MTN Rwanda	unregistered	Admin	2025-03-14 03:17:24.471872	\N
91	8901270332226050	0787288666	MTN Rwanda	unregistered	Admin	2025-03-14 03:17:26.435087	\N
92	8901457444073506	0787653591	MTN Rwanda	unregistered	Admin	2025-03-14 07:41:18.866462	\N
93	8901296884235961	0787352352	MTN Rwanda	unregistered	Admin	2025-03-14 08:29:55.959305	\N
94	8901172834472303	0787963307	MTN Rwanda	unregistered	Admin	2025-03-14 08:53:13.608542	\N
95	8901902889074722	0787114505	MTN Rwanda	unregistered	Admin	2025-03-14 09:14:25.102231	\N
97	8901564175133306	0787937658	MTN Rwanda	unregistered	Admin	2025-03-17 03:00:54.398015	\N
98	8901155620840301	0787699039	MTN Rwanda	unregistered	Admin	2025-03-17 03:00:57.107651	\N
156	8901313847556763	0786787902	MTN	active	54	2025-04-22 01:15:45.492073	61
100	8901691950902415	0787387255	MTN Rwanda	unregistered	Admin	2025-03-17 11:53:34.192546	\N
101	8901909392006725	0787540429	MTN Rwanda	unregistered	Admin	2025-03-17 11:53:44.485077	\N
102	8901437916718726	0787386220	MTN Rwanda	unregistered	Admin	2025-03-17 11:53:54.131921	\N
103	8901596021988710	0787796231	MTN Rwanda	unregistered	Admin	2025-03-18 00:22:49.922781	\N
104	8901409675317646	0787684971	MTN Rwanda	unregistered	Admin	2025-03-18 00:22:57.296965	\N
105	8901631505362846	0787761814	MTN Rwanda	unregistered	Admin	2025-03-18 09:43:39.732978	\N
130	8901695622409502	SWP_1744070543	MTN	swapped	54	2025-04-05 03:27:58.691527	56
141	8901554522579976	0783437740	MTN	active	Agent	2025-04-08 09:02:23.400241	56
125	8901162439021695	SWP_1744073866	MTN	swapped	54	2025-04-01 07:41:34.866017	55
142	8901569377994495	0782409658	Airtel	active	54	2025-04-08 09:57:46.208267	55
108	8901487702808011	0787444818	MTN Rwanda	active	Admin	2025-03-18 12:29:05.219635	\N
157	8901858579226525	0787710926	MTN Rwanda	unregistered	Admin	2025-04-25 08:34:50.055613	\N
143	8901946394441134	SWP_1744075366	MTN	swapped	54	2025-04-08 10:18:43.233269	\N
144	8901497901168751	0788599992	MTN	active	54	2025-04-08 10:22:46.856781	\N
145	8901789998439540	0787939734	MTN Rwanda	unregistered	Admin	2025-04-11 02:20:07.157971	\N
113	8901735469825267	0787165446	MTN Rwanda	unregistered	Admin	2025-03-21 05:54:00.909623	\N
114	8901518527783090	0787985400	MTN Rwanda	unregistered	Admin	2025-03-21 05:54:04.335138	\N
115	8901550770990614	0787261711	MTN Rwanda	unregistered	Admin	2025-03-21 05:54:05.972	\N
116	8901735764193295	0787789013	MTN Rwanda	unregistered	Admin	2025-03-21 05:54:08.746019	\N
117	8901468895492231	0787264413	MTN Rwanda	unregistered	Admin	2025-03-23 11:30:45.871188	\N
118	8901291180692005	0787759052	MTN Rwanda	unregistered	Admin	2025-03-23 11:30:48.795952	\N
119	8901302585721479	0787593080	MTN	unregistered	40	2025-03-25 09:42:11.52351	\N
120	8901215060749627	0787124134	MTN Rwanda	unregistered	Admin	2025-03-27 00:31:54.5526	\N
121	8901624785735637	0786868895	MTN	unregistered	39	2025-03-27 02:43:37.8592	\N
122	8901530737122698	0787305770	MTN Rwanda	unregistered	Admin	2025-03-29 11:48:05.503308	\N
146	8901337151791352	0787408913	MTN Rwanda	active	Admin	2025-04-12 05:33:01.067057	57
123	8901945295332656	0787832379	MTN Rwanda	active	Admin	2025-04-01 07:18:32.82291	54
124	8901966624971858	0787230570	MTN Rwanda	unregistered	Admin	2025-04-01 07:40:02.46385	\N
147	8901183383756135	0787955541	MTN Rwanda	unregistered	Admin	2025-04-14 01:00:47.030314	\N
168	8901854931425236	0787373658	MTN Rwanda	unregistered	Admin	2025-05-05 05:48:52.044301	\N
126	8901546922096255	0787516293	MTN Rwanda	unregistered	Admin	2025-04-01 09:31:41.756695	\N
127	8901290407796118	0787263404	MTN Rwanda	unregistered	Admin	2025-04-01 09:46:20.073995	\N
128	8901442723271245	0787461769	MTN Rwanda	unregistered	Admin	2025-04-01 09:50:16.805998	\N
129	8901593016321308	0787714618	MTN Rwanda	unregistered	Admin	2025-04-01 09:59:16.159967	\N
173	8901909162366461	0781978702	MTN	unregistered	54	2025-05-12 08:12:45.182347	\N
131	8901120417651201	0787122060	MTN Rwanda	unregistered	Admin	2025-04-06 23:58:37.511928	\N
132	8901701253445681	0787843442	MTN Rwanda	unregistered	Admin	2025-04-06 23:59:00.396955	\N
133	8901491810839928	0787749473	MTN Rwanda	unregistered	Admin	2025-04-06 23:59:02.256476	\N
134	8901342615731762	0787532566	MTN Rwanda	unregistered	Admin	2025-04-06 23:59:35.988604	\N
135	8901920323500613	0787454996	MTN Rwanda	unregistered	Admin	2025-04-07 08:24:34.493417	\N
136	8901297691704415	0787917284	MTN Rwanda	unregistered	Admin	2025-04-07 09:12:14.982672	\N
137	8901429096472713	0787535708	MTN Rwanda	unregistered	Admin	2025-04-07 09:20:15.219929	\N
138	8901846825173412	0787316567	MTN Rwanda	unregistered	Admin	2025-04-08 03:17:26.42743	\N
148	8901116929959108	0787195372	MTN	active	57	2025-04-15 06:18:28.216318	58
160	8901765884990587	SWP_1746575630	MTN	swapped	54	2025-04-30 07:56:58.673353	69
161	8901119623841129	0784690255	MTN	active	54	2025-05-07 08:53:50.37629	69
149	8901774409043052	0785796308	MTN	active	54	2025-04-16 06:37:12.534192	59
150	8901966840503626	0787804967	MTN Rwanda	unregistered	Admin	2025-04-16 10:13:19.731455	\N
151	8901393980322340	0787390971	MTN Rwanda	unregistered	Admin	2025-04-16 10:15:27.685624	\N
152	8901872233826917	0787344458	MTN Rwanda	unregistered	Admin	2025-04-16 10:34:02.684735	\N
153	8901326347934792	0787569319	MTN Rwanda	unregistered	Admin	2025-04-16 10:47:07.785357	\N
154	8901403627430297	0786916489	MTN	active	54	2025-04-17 06:59:03.191129	60
155	8901421439883836	0787178968	MTN Rwanda	unregistered	Admin	2025-04-17 07:50:55.397257	\N
159	8901257170530088	SWP_1746578960	MTN	swapped	54	2025-04-28 01:28:16.604163	\N
162	8901270367573968	0787880352	MTN Rwanda	unregistered	Admin	2025-05-02 03:44:29.400132	\N
163	8901700990955679	0787947145	MTN	unregistered	56	2025-05-02 04:35:57.90888	\N
164	8901881337582643	0787622098	MTN Rwanda	unregistered	Admin	2025-05-02 04:52:24.838277	\N
165	8901906398734427	0787280664	MTN Rwanda	unregistered	Admin	2025-05-03 13:45:57.467684	\N
166	8901898354917681	0787609027	MTN Rwanda	unregistered	Admin	2025-05-05 02:20:59.738641	\N
167	8901958464474132	0787657484	MTN Rwanda	unregistered	Admin	2025-05-05 05:48:35.033076	\N
169	8901612403911700	0787167297	MTN	active	54	2025-05-07 09:49:20.80047	\N
171	8901639177604566	0787611277	MTN Rwanda	unregistered	Admin	2025-05-07 10:16:15.700715	\N
158	8901871711562650	SWP_1746903137_6b84	MTN	swapped	54	2025-04-25 11:29:22.208758	62
170	8901669232128606	0782858063	MTN	active	user-62	2025-05-11 03:52:17.67445	62
172	8901839465275236	0789996968	MTN	active	54	2025-05-12 00:46:54.271282	70
\.


--
-- Data for Name: tenant_users; Type: TABLE DATA; Schema: public; Owner: ztn
--

COPY public.tenant_users (id, tenant_id, user_id, company_email, password_hash, created_at) FROM stdin;
1	2	57	alice@mohealth.rw	scrypt:32768:8:1$UD4YPexDDGVQeaWR$a5a611c3c61cb93a698dd850c76df9277840676502f5ef72812de30e8d419d14d60d50ab7cd41e95ed7f0ee69dd6c99f952f4b781a46b2ccae10d546418a2d6f	2025-04-26 08:02:05.619322
2	2	58	kamanzi@mohealth.rw	scrypt:32768:8:1$KXqsAyNAnSd9ZY5B$b8cde764fc3e80a183736842a780581b501dcc49df8251281a817e0406597fd458a2269d11f191a12adc10f7e015408815e882c6cf418062af066bbb6274c878	2025-04-26 08:05:42.420886
3	3	57	alice@edutech.rw	scrypt:32768:8:1$hW8Flqb42WMt635F$209421cdcfcffa0e2c6ee5b8404439255e4bec2f0a6f74f9b9a0059c47a3892fdfc726531ac08a04e78bc426e4bdb582c96415b3dbcdb82994ab023e5b67abaf	2025-04-26 08:10:03.004196
4	3	57	niyo@edutech.rw	scrypt:32768:8:1$CjFriONHjfDjr9we$a337ce6445e22f3be81e56002ab9cafb201d342288e9414225ec472138d14216ac9de5de551977d98e18812419e722772472d8de706a1f99b6edd6c5699f8782	2025-04-26 08:11:36.123859
5	2	56	john@mohealth.rw	scrypt:32768:8:1$qsfPkYUTjrpK2OMw$f6b4f04e227b77f21b2ab127ec4208fedb4038eb271b232714b0d61ec957ff4e9904b8b4db3bd5ab86cbbc3aa0679bb17686eaa642c1afd4924d5c1f6bfd60c9	2025-04-26 14:16:08.509613
\.


--
-- Data for Name: tenants; Type: TABLE DATA; Schema: public; Owner: ztn
--

COPY public.tenants (id, name, api_key, contact_email, plan, created_at) FROM stdin;
1	DummyTenant	dummyapikey123456	\N	\N	2025-04-26 14:05:29.315538
2	MinistryOfHealth	mohealthapikey987654	\N	premium	2025-04-26 05:07:08.632932
3	EduTechPlatform	edutechapikey2025	\N	free	2025-04-26 05:07:08.668881
\.


--
-- Data for Name: transactions; Type: TABLE DATA; Schema: public; Owner: ztn
--

COPY public.transactions (id, user_id, amount, transaction_type, status, "timestamp", location, device_info, fraud_flag, risk_score, transaction_metadata, tenant_id) FROM stdin;
163	55	10000	float_received	completed	2025-04-01 12:08:12.241944	{"lat": 34.7314935, "lng": 135.7347093}	{"platform": "Linux x86_64", "userAgent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Mobile Safari/537.36", "screen": {"width": 944, "height": 756}}	f	0	{"from_admin": "22", "approved_by": "admin", "float_source": "HQ Wallet"}	1
164	55	1000	withdrawal	completed	2025-04-01 12:13:27.386749	34.7315, 135.7347	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36	f	0	{"initiated_by": "user", "approved_by_agent": true, "assigned_agent_id": 54, "assigned_agent_mobile": "0787832379", "assigned_agent_name": "pathos muta", "approved_by": 54, "approved_at": "2025-04-01T12:14:36.392053"}	1
165	55	10	withdrawal	completed	2025-04-05 03:17:43.190201	34.7324, 135.7409	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	f	0	{"initiated_by": "user", "approved_by_agent": true, "assigned_agent_id": 54, "assigned_agent_mobile": "0787832379", "assigned_agent_name": "pathos muta", "approved_by": 54, "approved_at": "2025-04-05T03:22:29.316336"}	1
166	55	10	withdrawal	rejected	2025-04-05 03:17:53.825194	34.7324, 135.7409	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	f	0	{"initiated_by": "user", "approved_by_agent": false, "assigned_agent_id": 54, "assigned_agent_mobile": "0787832379", "assigned_agent_name": "pathos muta", "rejected_by_agent": true, "rejected_by": 54, "rejected_at": "2025-04-05T03:22:46.383571"}	1
167	54	20000	float_received	completed	2025-04-05 03:34:03.510026	{"lat": 34.7324314, "lng": 135.7408554}	{"platform": "Linux x86_64", "userAgent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0", "screen": {"width": 1366, "height": 768}}	f	0	{"from_admin": "22", "approved_by": "admin", "float_source": "HQ Wallet"}	1
168	56	3000	deposit	completed	2025-04-05 03:36:08.996677	\N	\N	f	0	{"deposited_by_mobile": "0787832379", "recipient_mobile": "0783437740", "recipient_name": "Gabriel Darwin"}	1
169	54	90	transfer	completed	2025-04-05 06:01:19.302906	\N	\N	f	0	{"transfer_by": "Agent", "recipient_mobile": "0783437740", "recipient_name": "Gabriel Darwin"}	1
170	55	100	deposit	completed	2025-04-05 07:28:16.665221	\N	\N	f	0	{"deposited_by_mobile": "0787832379", "recipient_mobile": "0782409658", "recipient_name": "Dary Betty"}	1
171	55	1000	transfer	completed	2025-04-05 07:38:18.97077	34.7321, 135.7355	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	f	0	{"recipient_mobile": "0787832379", "recipient_id": 54, "recipient_name": "pathos muta", "sender_id": 55}	1
172	56	700	withdrawal	expired	2025-04-05 08:11:17.18429	34.7321, 135.7355	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	f	0	{"initiated_by": "user", "approved_by_agent": false, "assigned_agent_id": 54, "assigned_agent_mobile": "0787832379", "assigned_agent_name": "pathos muta"}	1
176	55	100000	transfer	pending	2025-04-07 11:21:34.103537	Kigali	TestDevice/1.0	t	0.85	{"test_injected": true}	1
177	56	160	transfer	completed	2025-04-07 02:42:53.002621	34.7341, 135.7414	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	f	0.4	{"recipient_mobile": "0782409658", "recipient_id": 55, "recipient_name": "Dary Betty", "sender_id": 56}	1
178	56	100	transfer	completed	2025-04-07 02:48:20.417474	34.7341, 135.7414	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	f	0.4	{"recipient_mobile": "0782409658", "recipient_id": 55, "recipient_name": "Dary Betty", "sender_id": 56}	1
175	56	200	withdrawal	expired	2025-04-07 02:05:20.076273	34.7341, 135.7414	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	f	0.4	{"initiated_by": "user", "approved_by_agent": false, "assigned_agent_id": 54, "assigned_agent_mobile": "0787832379", "assigned_agent_name": "pathos muta"}	1
174	56	200	withdrawal	expired	2025-04-07 02:05:17.154179	34.7341, 135.7414	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	f	0.4	{"initiated_by": "user", "approved_by_agent": false, "assigned_agent_id": 54, "assigned_agent_mobile": "0787832379", "assigned_agent_name": "pathos muta"}	1
173	55	10	withdrawal	expired	2025-04-07 01:24:15.453619	34.7341, 135.7414	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	f	0.4	{"initiated_by": "user", "approved_by_agent": false, "assigned_agent_id": 54, "assigned_agent_mobile": "0787832379", "assigned_agent_name": "pathos muta"}	1
179	55	2000	transfer	completed	2025-04-07 10:10:57.454655	34.7341, 135.7414	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	f	0	{"recipient_mobile": "0783437740", "recipient_id": 56, "recipient_name": "Gabriel Darwin", "sender_id": 55}	1
180	55	892	withdrawal	rejected	2025-04-07 10:42:19.577005	34.7341, 135.7414	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	f	0	{"initiated_by": "user", "approved_by_agent": false, "assigned_agent_id": 54, "assigned_agent_mobile": "0787832379", "assigned_agent_name": "pathos muta", "rejected_by_agent": true, "rejected_by": 54, "rejected_at": "2025-04-07T10:46:51.499295"}	1
181	55	100	transfer	completed	2025-04-07 11:03:21.157567	34.7341, 135.7414	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	f	0	{"recipient_mobile": "0783437740", "recipient_id": 56, "recipient_name": "Gabriel Darwin", "sender_id": 55}	1
182	55	200	withdrawal	expired	2025-04-07 11:13:16.041238	34.7341, 135.7414	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	f	0	{"initiated_by": "user", "approved_by_agent": false, "assigned_agent_id": 54, "assigned_agent_mobile": "0787832379", "assigned_agent_name": "pathos muta"}	1
183	56	100	deposit	completed	2025-04-08 02:26:18.784899	\N	\N	f	0	{"deposited_by_mobile": "0787832379", "recipient_mobile": "0783437740", "recipient_name": "Gabriel Darwin"}	1
184	54	100	transfer	completed	2025-04-08 02:28:47.241427	\N	\N	f	0	{"transfer_by": "Agent", "recipient_mobile": "0782409658", "recipient_name": "Dary Betty"}	1
185	54	100	withdrawal	completed	2025-04-08 02:31:28.497267	\N	\N	f	0	{"withdrawal_method": "Agent Processed"}	1
186	56	1000	withdrawal	completed	2025-04-08 03:14:17.853818		Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	f	0	{"initiated_by": "user", "approved_by_agent": true, "assigned_agent_id": 54, "assigned_agent_mobile": "0787832379", "assigned_agent_name": "pathos muta", "approved_by": 54, "approved_at": "2025-04-08T03:15:44.303381"}	1
187	55	100	withdrawal	rejected	2025-04-08 06:15:50.872378		Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	f	0	{"initiated_by": "user", "approved_by_agent": false, "assigned_agent_id": 54, "assigned_agent_mobile": "0787832379", "assigned_agent_name": "pathos muta", "rejected_by_agent": true, "rejected_by": 54, "rejected_at": "2025-04-08T06:17:59.749811"}	1
188	55	1000	reversal	completed	2025-04-08 11:04:10.320061	Admin Panel	Admin HQ	f	0	{"reversal_of_transaction_id": 171, "original_sender": 55, "original_recipient": 54, "reversed_by_admin": "22"}	1
189	55	1000	reversal	completed	2025-04-08 11:04:40.466227	Admin Panel	Admin HQ	f	0	{"reversal_of_transaction_id": 171, "original_sender": 55, "original_recipient": 54, "reversed_by_admin": "22"}	1
190	56	2000	transfer	completed	2025-04-08 11:11:57.765242		Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	f	0	{"recipient_mobile": "0782409658", "recipient_id": 55, "recipient_name": "Dary Betty", "sender_id": 56}	1
191	56	2000	reversal	pending	2025-04-08 11:12:27.328901	\N	\N	f	0	{"reversal_of_transaction_id": 190, "original_sender": 56, "original_recipient": 55, "reversed_by_admin": "22", "delayed_refund": true}	1
192	55	2000	withdrawal	rejected	2025-04-09 07:12:12.317769	34.7341, 135.7414	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	f	0	{"initiated_by": "user", "approved_by_agent": false, "assigned_agent_id": 54, "assigned_agent_mobile": "0787832379", "assigned_agent_name": "pathos muta", "rejected_by_agent": true, "rejected_by": 54, "rejected_at": "2025-04-09T07:14:11.264705"}	1
193	55	2000	transfer	completed	2025-04-11 01:10:22.391788	34.7308, 135.7480	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	f	0	{"recipient_mobile": "0783437740", "recipient_id": 56, "recipient_name": "Gabriel Darwin", "sender_id": 55}	1
194	55	2000	reversal	pending	2025-04-11 01:10:48.974068	\N	\N	f	0	{"reversal_of_transaction_id": 193, "original_sender": 55, "original_recipient": 56, "reversed_by_admin": "22", "delayed_refund": true}	1
195	55	200	transfer	completed	2025-04-11 01:37:20.378877	34.7308, 135.7480	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	f	0	{"recipient_mobile": "0783437740", "recipient_id": 56, "recipient_name": "Gabriel Darwin", "sender_id": 55}	1
196	55	200	reversal	pending	2025-04-11 01:37:46.444703	\N	\N	f	0	{"reversal_of_transaction_id": 195, "original_sender": 55, "original_recipient": 56, "reversed_by_admin": "22", "delayed_refund": true}	1
197	55	50	transfer	completed	2025-04-11 01:43:14.278625	34.7308, 135.7480	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	f	0	{"recipient_mobile": "0783437740", "recipient_id": 56, "recipient_name": "Gabriel Darwin", "sender_id": 55}	1
198	55	50	reversal	completed	2025-04-11 01:43:41.444538	\N	\N	f	0	{"reversal_of_transaction_id": 197, "original_sender": 55, "original_recipient": 56, "reversed_by_admin": "22", "delayed_refund": true}	1
199	55	1150	transfer	completed	2025-04-11 01:46:29.447016	34.7308, 135.7480	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	f	0	{"recipient_mobile": "0783437740", "recipient_id": 56, "recipient_name": "Gabriel Darwin", "sender_id": 55}	1
200	55	1150	reversal	completed	2025-04-11 01:48:57.76803	\N	\N	f	0	{"reversal_of_transaction_id": 199, "original_sender": 55, "original_recipient": 56, "reversed_by_admin": "22", "delayed_refund": true}	1
201	56	100	deposit	completed	2025-04-11 02:04:54.709163	\N	\N	f	0	{"deposited_by_mobile": "0787832379", "recipient_mobile": "0783437740", "recipient_name": "Gabriel Darwin"}	1
202	54	200	transfer	completed	2025-04-11 02:14:48.391624	\N	\N	f	0	{"transfer_by": "Agent", "recipient_mobile": "0783437740", "recipient_name": "Gabriel Darwin"}	1
203	56	1000	withdrawal	expired	2025-04-11 02:23:13.120218	34.7315, 135.7347	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	f	0	{"initiated_by": "user", "approved_by_agent": false, "assigned_agent_id": 54, "assigned_agent_mobile": "0787832379", "assigned_agent_name": "pathos muta"}	1
206	54	5000	float_received	completed	2025-04-14 01:16:59.764531	{"lat": 34.7308032, "lng": 135.7479936}	{"platform": "Linux x86_64", "userAgent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36", "screen": {"width": 944, "height": 756}}	f	0	{"from_admin": "22", "approved_by": "admin", "float_source": "HQ Wallet"}	1
207	55	7839	deposit	completed	2025-04-25 08:30:26.158193	\N	\N	f	0	{"deposited_by_mobile": "0787832379", "recipient_mobile": "0782409658", "recipient_name": "Dary Betty"}	1
209	69	1000	deposit	completed	2025-05-02 03:26:10.115323	\N	\N	f	0	{"deposited_by_mobile": "0787832379", "recipient_mobile": "0784690255", "recipient_name": "bztn Lab"}	1
211	69	100	transfer	completed	2025-05-02 03:35:12.050981	34.7315, 135.7347	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	f	0	{"recipient_mobile": "0783437740", "recipient_id": 56, "recipient_name": "Gabriel Darwin", "sender_id": 69}	1
210	69	200	withdrawal	completed	2025-05-02 03:33:47.50181	34.7315, 135.7347	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	f	0	{"initiated_by": "user", "approved_by_agent": true, "assigned_agent_id": 54, "assigned_agent_mobile": "0787832379", "assigned_agent_name": "Pathos Mut", "approved_by": 54, "approved_at": "2025-05-02T03:36:40.670952"}	1
212	54	30000	float_received	completed	2025-05-02 03:45:24.787162	{"lat": 34.7314883, "lng": 135.7347076}	{"platform": "Linux x86_64", "userAgent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36", "screen": {"width": 1360, "height": 768}}	f	0	{"from_admin": "22", "approved_by": "admin", "float_source": "HQ Wallet"}	1
213	69	500	deposit	completed	2025-05-02 04:40:54.715179	\N	\N	f	0	{"deposited_by_mobile": "SWP_1744070543", "recipient_mobile": "0784690255", "recipient_name": "bztn Lab"}	1
214	69	100	reversal	completed	2025-05-02 04:47:16.11542	\N	\N	f	0	{"reversal_of_transaction_id": 211, "original_sender": 69, "original_recipient": 56, "reversed_by_admin": "22", "delayed_refund": true}	1
215	69	1000	float_received	completed	2025-05-05 02:24:52.973452	{"lat": 35.6916, "lng": 139.768}	{"platform": "Linux x86_64", "userAgent": "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0", "screen": {"width": 1296, "height": 660}}	f	0	{"from_admin": "22", "approved_by": "admin", "float_source": "HQ Wallet"}	1
216	55	1000	withdrawal	pending	2025-05-05 07:26:00.553992		Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	f	0	{"initiated_by": "user", "approved_by_agent": false, "assigned_agent_id": 54, "assigned_agent_mobile": "0787832379", "assigned_agent_name": "Pathos Mut"}	1
\.


--
-- Data for Name: user_access_controls; Type: TABLE DATA; Schema: public; Owner: ztn
--

COPY public.user_access_controls (id, user_id, role_id, access_level) FROM stdin;
7	22	1	admin
51	54	2	read
52	55	3	read
54	57	2	read
55	58	3	read
56	59	3	read
57	60	3	read
58	61	3	read
59	62	3	read
53	56	2	read
60	69	2	read
61	70	3	read
\.


--
-- Data for Name: user_auth_logs; Type: TABLE DATA; Schema: public; Owner: ztn
--

COPY public.user_auth_logs (id, user_id, auth_method, auth_status, auth_timestamp, ip_address, location, device_info, failed_attempts, geo_trust_score, tenant_id) FROM stdin;
1175	22	password	success	2025-04-26 14:27:41.758184	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1194	57	password	success	2025-04-26 21:53:15.826154	127.0.0.1	Unknown	IAMaaS API Access	0	0.5	3
1195	57	password	success	2025-04-26 21:56:09.853146	127.0.0.1	Unknown	IAMaaS API Access	0	0.5	2
1196	57	password	success	2025-04-26 21:56:34.412565	127.0.0.1	Unknown	IAMaaS API Access	0	0.5	2
1197	57	password	success	2025-04-26 21:59:11.817181	127.0.0.1	Unknown	IAMaaS API Access	0	0.5	2
1198	57	password	success	2025-04-26 22:09:46.442527	127.0.0.1	Unknown	IAMaaS API Access	0	0.5	2
1199	57	password	success	2025-04-26 22:15:44.574756	127.0.0.1	Unknown	IAMaaS API Access	0	0.5	2
1200	57	password	success	2025-04-26 22:23:36.878658	127.0.0.1	Unknown	IAMaaS API Access	0	0.5	2
1201	57	password	success	2025-04-26 22:28:18.496373	127.0.0.1	Unknown	IAMaaS API Access	0	0.5	2
1202	57	password	success	2025-04-26 22:35:35.215535	127.0.0.1	Unknown	IAMaaS API Access	0	0.5	2
1203	57	password	success	2025-04-26 22:50:33.276548	127.0.0.1	Unknown	IAMaaS API Access	0	0.5	2
1207	56	password	success	2025-04-27 18:34:14.32898	127.0.0.1	Unknown	IAMaaS API Access	0	0.5	2
1245	54	password	success	2025-04-28 10:22:53.195527	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1246	54	totp	success	2025-04-28 10:23:37.702615	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1247	54	webauthn	success	2025-04-28 10:24:21.759636	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1249	54	password	failed	2025-04-28 10:38:41.95163	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	2	0.5	1
1257	22	password	success	2025-04-30 15:43:38.246666	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1258	22	totp	success	2025-04-30 15:43:55.668771	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1259	22	webauthn	success	2025-04-30 15:44:36.169077	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1260	54	password	failed	2025-04-30 15:47:21.239361	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	1	0.5	1
1262	54	password	failed	2025-04-30 15:47:24.079334	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	3	0.5	1
1264	54	password	failed	2025-04-30 15:47:27.40889	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	5	0.5	1
1292	69	password	success	2025-05-02 11:42:17.457601	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1293	69	totp	success	2025-05-02 11:42:38.637181	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1294	69	webauthn	success	2025-05-02 11:43:08.000875	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1295	54	password	failed	2025-05-02 11:46:14.857823	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	1	0.5	1
1297	54	totp	success	2025-05-02 11:46:39.800112	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1298	54	webauthn	success	2025-05-02 11:47:20.518534	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1323	56	password	failed	2025-05-03 20:43:53.420264	192.168.60.3	Unknown	Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0	1	0.5	1
1324	56	password	success	2025-05-03 20:44:11.89617	192.168.60.3	Unknown	Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0	0	0.5	1
1325	56	totp	success	2025-05-03 20:44:37.43287	192.168.60.3	Unknown	Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0	0	0.5	1
1326	54	password	failed	2025-05-03 20:48:07.019231	192.168.60.7	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	1	0.5	1
1327	54	password	success	2025-05-03 20:48:10.910136	192.168.60.7	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1328	54	totp	success	2025-05-03 20:48:22.621954	192.168.60.7	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1382	22	password	success	2025-05-05 10:38:25.355293	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1383	22	totp	success	2025-05-05 10:38:41.843997	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1384	22	webauthn	success	2025-05-05 10:39:08.388829	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1385	22	password	success	2025-05-05 11:19:08.546317	192.168.2.116	Unknown	Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0	0	0.5	1
1389	22	totp	failed	2025-05-05 11:36:30.036797	192.168.2.116	Unknown	Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0	1	0.5	1
1393	54	totp	success	2025-05-05 11:51:28.014857	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1394	54	webauthn	success	2025-05-05 11:51:45.544415	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1401	54	password	success	2025-05-05 12:28:05.873693	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	0	0.5	1
1403	54	webauthn	success	2025-05-05 12:28:25.653092	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	0	0.5	1
1447	22	password	success	2025-05-06 12:31:25.256394	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1448	22	totp	success	2025-05-06 12:31:46.740607	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1176	22	totp	success	2025-04-26 14:32:37.84901	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1204	57	password	success	2025-04-26 23:03:06.294382	127.0.0.1	Unknown	IAMaaS API Access	0	0.5	2
1205	58	password	success	2025-04-26 23:05:28.768252	127.0.0.1	Unknown	IAMaaS API Access	0	0.5	2
1206	56	password	success	2025-04-26 23:18:09.629597	127.0.0.1	Unknown	IAMaaS API Access	0	0.5	2
1208	56	password	success	2025-04-27 19:01:08.341662	127.0.0.1	Unknown	IAMaaS API Access	0	0.5	2
1209	56	password	success	2025-04-27 19:01:59.348842	127.0.0.1	Unknown	IAMaaS API Access	0	0.5	2
1210	56	password	success	2025-04-27 19:06:30.396995	127.0.0.1	Unknown	IAMaaS API Access	0	0.5	2
1211	54	password	failed	2025-04-27 19:12:28.795755	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	1	0.5	1
1212	54	password	failed	2025-04-27 19:12:36.785175	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	2	0.5	1
1213	54	password	success	2025-04-27 19:12:47.844923	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
1214	54	totp	success	2025-04-27 19:13:06.603166	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
1215	54	webauthn	success	2025-04-27 19:13:42.944035	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
1216	56	password	failed	2025-04-27 19:14:29.32411	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	1	0.5	1
1222	22	password	failed	2025-04-27 19:20:59.055582	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	2	0.5	1
1226	54	password	failed	2025-04-27 19:29:52.572176	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	3	0.5	1
1230	22	password	success	2025-04-27 19:46:23.597566	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1232	22	webauthn	success	2025-04-27 19:46:47.408822	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1248	54	password	failed	2025-04-28 10:38:40.754004	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	1	0.5	1
1252	54	password	failed	2025-04-28 10:38:44.077104	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	5	0.5	1
1261	54	password	failed	2025-04-30 15:47:22.649783	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	2	0.5	1
1263	54	password	failed	2025-04-30 15:47:25.884575	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	4	0.5	1
1296	54	password	success	2025-05-02 11:46:26.159881	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1329	22	password	success	2025-05-03 21:38:57.914478	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0	0	0.5	1
1330	22	totp	failed	2025-05-03 21:39:25.342776	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0	1	0.5	1
1331	22	totp	success	2025-05-03 21:39:47.414061	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0	0	0.5	1
1332	22	password	success	2025-05-03 21:46:30.988519	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1333	22	totp	success	2025-05-03 21:46:54.030896	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1386	22	totp	success	2025-05-05 11:19:27.607634	192.168.2.116	Unknown	Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0	0	0.5	1
1387	22	webauthn	success	2025-05-05 11:19:33.919558	192.168.2.116	Unknown	Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0	0	0.5	1
1388	22	password	success	2025-05-05 11:36:13.784218	192.168.2.116	Unknown	Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0	0	0.5	1
1390	22	totp	success	2025-05-05 11:36:43.194893	192.168.2.116	Unknown	Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0	0	0.5	1
1391	22	webauthn	success	2025-05-05 11:36:48.746354	192.168.2.116	Unknown	Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0	0	0.5	1
1392	54	password	success	2025-05-05 11:51:14.03646	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1399	22	totp	success	2025-05-05 12:02:10.774086	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	0	0.5	1
1449	22	webauthn	success	2025-05-06 12:32:36.554142	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1177	22	password	success	2025-04-26 14:44:11.928301	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1178	22	totp	success	2025-04-26 14:44:27.143102	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1179	22	webauthn	success	2025-04-26 14:44:32.545087	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1181	54	password	failed	2025-04-26 14:46:07.361276	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	2	0.5	1
1183	54	totp	success	2025-04-26 14:46:37.369804	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1184	54	webauthn	success	2025-04-26 14:46:42.665233	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1186	59	totp	failed	2025-04-26 14:47:47.005951	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	1	0.5	1
1217	56	password	failed	2025-04-27 19:14:42.430352	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	2	0.5	1
1223	22	password	failed	2025-04-27 19:22:40.639793	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	3	0.5	1
1227	54	password	success	2025-04-27 19:30:06.502055	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
1229	54	webauthn	success	2025-04-27 19:30:54.536707	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
1250	54	password	failed	2025-04-28 10:38:42.696302	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	3	0.5	1
1253	22	password	success	2025-04-28 10:39:15.980676	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1256	56	password	success	2025-04-28 10:57:58.517799	127.0.0.1	Unknown	IAMaaS API Access	0	0.5	2
1265	22	password	success	2025-04-30 16:27:15.84037	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1266	22	totp	success	2025-04-30 16:28:44.054254	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1267	22	webauthn	success	2025-04-30 16:30:12.666923	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1268	61	password	failed	2025-04-30 16:37:54.298926	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	1	0.5	1
1271	54	totp	success	2025-04-30 16:39:38.143924	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1272	54	webauthn	success	2025-04-30 16:39:46.726083	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1299	54	password	success	2025-05-02 12:08:52.718301	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1300	54	totp	success	2025-05-02 12:09:09.674025	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1301	54	webauthn	success	2025-05-02 12:09:14.642298	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1334	22	password	success	2025-05-03 22:13:38.424913	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0	0	0.5	1
1335	22	totp	success	2025-05-03 22:14:27.938796	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0	0	0.5	1
1395	54	password	success	2025-05-05 11:53:51.402211	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	0	0.5	1
1397	54	webauthn	success	2025-05-05 11:54:14.208632	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	0	0.5	1
1398	22	password	success	2025-05-05 12:01:52.65242	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	0	0.5	1
1400	22	webauthn	success	2025-05-05 12:02:16.892367	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	0	0.5	1
1450	22	password	success	2025-05-06 12:49:21.953048	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	0	0.5	1
1451	22	totp	success	2025-05-06 12:49:41.677389	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	0	0.5	1
1452	22	webauthn	success	2025-05-06 12:49:48.013572	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	0	0.5	1
1453	22	password	success	2025-05-06 13:07:10.053422	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	0	0.5	1
1456	54	password	success	2025-05-07 17:29:41.728928	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1457	54	totp	success	2025-05-07 17:29:59.193206	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1458	54	webauthn	success	2025-05-07 17:30:25.517161	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1472	22	password	success	2025-05-08 11:32:13.432148	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1473	22	totp	success	2025-05-08 11:32:26.342188	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1474	22	webauthn	success	2025-05-08 11:33:17.673462	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1475	62	password	failed	2025-05-08 11:35:30.875608	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	1	0.5	1
1477	62	password	failed	2025-05-08 11:35:45.69417	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	3	0.5	1
1180	54	password	failed	2025-04-26 14:45:55.99506	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	1	0.5	1
1182	54	password	success	2025-04-26 14:46:12.377917	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1185	59	password	success	2025-04-26 14:47:09.930462	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1218	56	password	failed	2025-04-27 19:15:03.013381	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	3	0.5	1
1228	54	totp	success	2025-04-27 19:30:48.195287	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
1231	22	totp	success	2025-04-27 19:46:40.656636	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1251	54	password	failed	2025-04-28 10:38:43.363105	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	4	0.5	1
1254	22	totp	success	2025-04-28 10:39:38.998302	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1255	22	webauthn	success	2025-04-28 10:39:44.890476	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1269	61	password	failed	2025-04-30 16:38:01.962307	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	2	0.5	1
1270	54	password	success	2025-04-30 16:39:22.269227	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1302	54	password	success	2025-05-02 12:25:19.865623	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1303	54	totp	success	2025-05-02 12:25:39.929707	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1304	54	webauthn	success	2025-05-02 12:25:44.762645	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1336	22	password	success	2025-05-03 22:18:52.592977	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1337	22	totp	success	2025-05-03 22:19:07.004002	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1338	22	webauthn	success	2025-05-03 22:19:13.407731	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1396	54	totp	success	2025-05-05 11:54:09.081705	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	0	0.5	1
1402	54	totp	success	2025-05-05 12:28:21.06053	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	0	0.5	1
1454	22	totp	success	2025-05-06 13:08:14.483257	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	0	0.5	1
1455	22	webauthn	success	2025-05-06 13:08:19.532466	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	0	0.5	1
1459	54	password	success	2025-05-07 17:52:28.585292	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Mobile Safari/537.36	0	0.5	1
1460	54	totp	success	2025-05-07 17:52:50.850633	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Mobile Safari/537.36	0	0.5	1
1461	54	webauthn	success	2025-05-07 17:52:56.002176	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Mobile Safari/537.36	0	0.5	1
1463	54	totp	success	2025-05-07 18:42:52.597496	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1476	62	password	failed	2025-05-08 11:35:37.736079	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	2	0.5	1
1478	62	password	success	2025-05-08 11:35:52.070212	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1479	54	password	success	2025-05-08 11:36:37.126768	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1187	59	totp	failed	2025-04-26 14:48:09.215732	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	2	0.5	1
1219	56	password	failed	2025-04-27 19:15:05.67518	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	4	0.5	1
1224	22	password	failed	2025-04-27 19:24:16.281676	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	4	0.5	1
1273	56	password	success	2025-04-30 16:48:54.15291	127.0.0.1	Unknown	IAMaaS API Access	0	0.5	2
1274	54	totp	success	2025-04-30 16:51:19.968422	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1275	54	password	success	2025-04-30 16:53:41.918299	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1276	54	totp	success	2025-04-30 16:54:38.631605	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1277	54	webauthn	success	2025-04-30 16:54:45.26679	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1305	69	password	success	2025-05-02 12:26:43.903429	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1307	69	webauthn	success	2025-05-02 12:27:08.075824	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1339	22	password	success	2025-05-03 22:32:39.080221	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1340	22	totp	success	2025-05-03 22:32:51.430501	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1341	22	webauthn	success	2025-05-03 22:32:57.03249	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1404	54	password	success	2025-05-05 12:54:34.756197	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	0	0.5	1
1405	54	totp	success	2025-05-05 12:54:56.889987	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	0	0.5	1
1406	54	webauthn	success	2025-05-05 12:55:02.009143	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	0	0.5	1
1462	54	password	success	2025-05-07 18:42:39.892721	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1464	54	webauthn	success	2025-05-07 18:42:57.283053	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1480	54	totp	success	2025-05-08 11:36:47.832364	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1481	54	webauthn	success	2025-05-08 11:36:52.715361	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1188	22	password	success	2025-04-26 16:11:39.44935	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1189	22	totp	success	2025-04-26 16:11:58.480708	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1190	22	webauthn	success	2025-04-26 16:12:04.446236	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1220	56	password	failed	2025-04-27 19:15:06.699079	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	5	0.5	1
1221	22	password	failed	2025-04-27 19:20:30.927032	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	1	0.5	1
1225	22	password	failed	2025-04-27 19:24:26.730792	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	5	0.5	1
1278	54	password	success	2025-04-30 17:04:00.380061	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	0	0.5	1
1306	69	totp	success	2025-05-02 12:26:57.863895	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1342	22	totp	success	2025-05-03 22:43:09.99136	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1343	22	webauthn	success	2025-05-03 22:43:15.218143	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1407	54	password	success	2025-05-05 13:12:04.588937	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	0	0.5	1
1408	54	totp	success	2025-05-05 13:12:23.197688	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	0	0.5	1
1409	54	webauthn	success	2025-05-05 13:12:28.536333	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	0	0.5	1
1465	54	totp	success	2025-05-07 18:56:20.708774	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Mobile Safari/537.36	0	0.5	1
1482	54	password	failed	2025-05-08 12:04:08.517915	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	1	0.5	1
1483	54	password	failed	2025-05-08 12:04:15.002132	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	2	0.5	1
1484	54	password	failed	2025-05-08 12:04:20.938852	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	3	0.5	1
1485	54	password	success	2025-05-08 12:04:41.93152	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1486	54	totp	success	2025-05-08 12:04:55.29794	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1487	54	webauthn	success	2025-05-08 12:05:01.296734	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1500	54	password	success	2025-05-11 10:23:48.375692	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1501	54	totp	success	2025-05-11 10:24:08.094877	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1502	54	webauthn	success	2025-05-11 10:24:37.176148	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1545	56	password	success	2025-05-12 09:38:22.313086	127.0.0.1	Unknown	IAMaaS API Access	0	0.5	2
216	56	totp	success	2025-04-11 15:44:14.42129	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
1191	58	password	success	2025-04-26 17:06:08.395846	127.0.0.1	Unknown	IAMaaS API Access	0	0.5	2
1233	22	password	success	2025-04-27 20:18:46.618513	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1234	22	password	success	2025-04-27 20:20:14.00674	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1235	22	password	success	2025-04-27 20:36:27.587038	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1236	22	totp	failed	2025-04-27 20:37:32.280232	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	1	0.5	1
1237	22	totp	success	2025-04-27 20:37:44.719592	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1238	22	webauthn	success	2025-04-27 20:37:53.03271	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1279	54	totp	success	2025-04-30 17:04:20.109015	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	0	0.5	1
1308	54	password	failed	2025-05-02 12:35:50.68333	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	2	0.5	1
1310	54	password	success	2025-05-02 12:36:02.849575	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1314	22	totp	success	2025-05-02 12:38:15.267985	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1344	54	password	failed	2025-05-03 22:44:05.770984	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	2	0.5	1
1345	54	password	success	2025-05-03 22:44:10.462517	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1346	54	totp	success	2025-05-03 22:44:22.780761	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1347	54	webauthn	success	2025-05-03 22:44:27.919292	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1348	22	password	success	2025-05-03 22:45:08.460592	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1350	22	webauthn	success	2025-05-03 22:45:24.848086	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1352	22	password	success	2025-05-03 22:47:30.586056	192.168.60.3	Unknown	Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0	0	0.5	1
1355	22	totp	success	2025-05-03 22:58:06.462811	192.168.60.3	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1358	22	totp	success	2025-05-03 22:59:15.64037	192.168.60.3	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1360	22	totp	success	2025-05-03 23:01:15.599446	192.168.60.3	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1362	22	totp	success	2025-05-03 23:02:08.366055	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1365	22	totp	success	2025-05-03 23:22:55.751439	192.168.60.3	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1373	22	totp	success	2025-05-04 00:00:52.335919	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1376	56	password	failed	2025-05-04 00:20:04.468049	192.168.60.3	Unknown	curl/8.13.0	3	0.5	1
1379	56	password	failed	2025-05-04 00:42:07.153095	192.168.60.3	Unknown	python-requests/2.32.3	6	0.5	1
1381	22	totp	success	2025-05-04 00:46:56.013989	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1410	22	password	success	2025-05-05 14:37:55.722487	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	0	0.5	1
1411	22	totp	success	2025-05-05 14:39:52.357916	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	0	0.5	1
1412	22	webauthn	success	2025-05-05 14:39:57.182772	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	0	0.5	1
1466	54	password	success	2025-05-07 18:58:23.640242	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Mobile Safari/537.36	0	0.5	1
1467	54	totp	success	2025-05-07 18:58:38.184255	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Mobile Safari/537.36	0	0.5	1
1468	54	webauthn	success	2025-05-07 18:58:43.482161	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Mobile Safari/537.36	0	0.5	1
1488	54	password	success	2025-05-08 13:03:41.279056	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1489	54	totp	success	2025-05-08 13:03:51.646911	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1490	54	webauthn	success	2025-05-08 13:03:56.22657	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1503	54	password	success	2025-05-11 10:41:17.29897	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1504	54	totp	success	2025-05-11 10:41:27.911256	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1505	54	webauthn	success	2025-05-11 10:41:32.766663	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1546	54	password	success	2025-05-12 09:39:45.885369	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1192	57	password	success	2025-04-26 17:28:16.070724	127.0.0.1	Unknown	IAMaaS API Access	0	0.5	3
1239	54	password	failed	2025-04-27 21:27:22.568236	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	4	0.5	1
1240	54	password	success	2025-04-27 21:27:29.210481	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1241	54	password	success	2025-04-27 21:29:07.201637	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1242	54	password	success	2025-04-27 21:30:17.509243	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1243	54	totp	success	2025-04-27 21:41:11.728423	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1244	54	webauthn	success	2025-04-27 21:41:17.891245	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1280	69	password	failed	2025-04-30 18:14:12.872761	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	1	0.5	1
1281	69	password	success	2025-04-30 18:14:20.315034	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
1309	54	password	failed	2025-05-02 12:35:58.019849	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	3	0.5	1
1311	54	totp	success	2025-05-02 12:36:19.899927	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1312	54	webauthn	success	2025-05-02 12:36:25.304769	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1315	22	webauthn	success	2025-05-02 12:38:20.075652	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1349	22	totp	success	2025-05-03 22:45:20.172998	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1353	22	totp	success	2025-05-03 22:47:44.643451	192.168.60.3	Unknown	Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0	0	0.5	1
1372	22	password	success	2025-05-04 00:00:37.176591	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1375	69	password	success	2025-05-04 00:14:00.634423	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1380	22	password	success	2025-05-04 00:46:04.284604	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1413	61	password	failed	2025-05-05 15:20:31.401665	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	1	0.5	1
1414	61	password	failed	2025-05-05 15:20:39.671554	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	2	0.5	1
1415	22	password	success	2025-05-05 15:20:53.201085	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	0	0.5	1
1416	22	totp	success	2025-05-05 15:21:09.437846	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	0	0.5	1
1417	22	webauthn	success	2025-05-05 15:21:16.205926	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	0	0.5	1
1418	55	password	failed	2025-05-05 15:21:50.283459	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	1	0.5	1
1420	55	password	failed	2025-05-05 15:22:02.260101	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	3	0.5	1
1422	55	password	success	2025-05-05 15:22:23.496791	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1424	55	totp	failed	2025-05-05 15:22:52.541905	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	2	0.5	1
1428	55	password	success	2025-05-05 15:26:22.673797	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	0	0.5	1
1431	55	password	success	2025-05-05 16:22:23.503761	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	0	0.5	1
1469	22	password	success	2025-05-07 19:14:29.09097	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Mobile Safari/537.36	0	0.5	1
1471	22	webauthn	success	2025-05-07 19:14:49.988775	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Mobile Safari/537.36	0	0.5	1
1491	54	password	success	2025-05-08 13:30:53.38977	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1492	54	totp	success	2025-05-08 13:31:11.565321	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1493	54	webauthn	success	2025-05-08 13:31:16.429148	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1506	54	password	success	2025-05-11 10:58:26.922583	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1507	54	totp	success	2025-05-11 10:58:42.395806	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1508	54	webauthn	success	2025-05-11 10:58:47.347225	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1547	54	totp	success	2025-05-12 09:40:12.934479	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1548	54	webauthn	success	2025-05-12 09:40:49.718791	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
334	56	totp	success	2025-04-12 13:27:04.885057	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
336	55	password	success	2025-04-12 13:27:49.710361	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
338	54	password	success	2025-04-12 13:29:54.255345	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
340	54	totp	success	2025-04-12 13:30:16.027063	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
342	56	password	success	2025-04-12 13:40:27.097404	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1193	57	password	success	2025-04-26 18:35:34.103292	127.0.0.1	Unknown	IAMaaS API Access	0	0.5	3
1282	22	password	success	2025-04-30 18:30:42.606044	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1283	22	totp	success	2025-04-30 18:31:09.756898	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1284	22	webauthn	success	2025-04-30 18:31:15.903353	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1313	22	password	success	2025-05-02 12:37:58.401055	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1351	22	password	failed	2025-05-03 22:47:16.817638	192.168.60.3	Unknown	Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0	1	0.5	1
1354	22	password	success	2025-05-03 22:57:45.283834	192.168.60.3	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1357	22	totp	failed	2025-05-03 22:59:00.955599	192.168.60.3	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	3	0.5	1
1359	22	password	success	2025-05-03 23:01:01.256211	192.168.60.3	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1361	22	password	success	2025-05-03 23:01:52.990234	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1363	22	webauthn	success	2025-05-03 23:02:15.521621	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1364	22	password	success	2025-05-03 23:22:25.961943	192.168.60.3	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1366	22	webauthn	success	2025-05-03 23:27:19.080859	192.168.60.3	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1371	56	password	failed	2025-05-03 23:59:58.568801	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	2	0.5	1
1419	55	password	failed	2025-05-05 15:21:56.742754	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	2	0.5	1
1421	55	password	failed	2025-05-05 15:22:08.015737	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	4	0.5	1
1423	55	totp	failed	2025-05-05 15:22:39.343936	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	1	0.5	1
1425	55	totp	success	2025-05-05 15:23:15.605844	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1426	55	webauthn	success	2025-05-05 15:23:22.733535	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1427	55	totp	failed	2025-05-05 15:25:52.361088	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Mobile Safari/537.36	3	0.5	1
1429	55	totp	success	2025-05-05 15:26:44.498571	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	0	0.5	1
1430	55	webauthn	success	2025-05-05 15:26:49.876933	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	0	0.5	1
1432	55	totp	success	2025-05-05 16:22:40.989656	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	0	0.5	1
1433	55	webauthn	success	2025-05-05 16:22:47.673653	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	0	0.5	1
1470	22	totp	success	2025-05-07 19:14:45.444255	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Mobile Safari/537.36	0	0.5	1
1494	54	password	success	2025-05-08 13:49:59.337179	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1495	54	totp	success	2025-05-08 13:50:13.908123	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1496	54	webauthn	success	2025-05-08 13:50:18.789271	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1509	54	password	success	2025-05-11 11:15:41.180607	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1510	54	totp	success	2025-05-11 11:15:51.418176	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1511	54	webauthn	success	2025-05-11 11:15:56.487048	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1549	56	password	failed	2025-05-12 09:52:56.394605	192.168.2.116	Unknown	python-requests/2.32.3	1	0.5	1
1550	56	password	failed	2025-05-12 09:52:56.750481	192.168.2.116	Unknown	python-requests/2.32.3	2	0.5	1
1551	56	password	failed	2025-05-12 09:52:57.119282	192.168.2.116	Unknown	python-requests/2.32.3	3	0.5	1
1552	56	password	failed	2025-05-12 09:52:57.495181	192.168.2.116	Unknown	python-requests/2.32.3	4	0.5	1
1553	56	password	failed	2025-05-12 09:52:57.871345	192.168.2.116	Unknown	python-requests/2.32.3	5	0.5	1
1285	22	password	success	2025-04-30 18:50:45.592354	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1286	22	totp	success	2025-04-30 18:51:07.628688	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1287	22	webauthn	success	2025-04-30 18:51:12.241141	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1316	56	password	success	2025-05-02 13:30:44.014828	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1317	56	totp	success	2025-05-02 13:31:39.525074	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1318	56	webauthn	success	2025-05-02 13:31:45.574478	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1319	69	password	failed	2025-05-02 13:42:30.825895	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	1	0.5	1
1356	22	totp	failed	2025-05-03 22:58:44.740846	192.168.60.3	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	2	0.5	1
1368	54	totp	success	2025-05-03 23:37:42.657538	192.168.60.3	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1370	54	password	failed	2025-05-03 23:56:42.766977	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	3	0.5	1
1374	22	webauthn	success	2025-05-04 00:02:18.048423	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1378	56	password	failed	2025-05-04 00:22:31.562193	192.168.60.3	Unknown	python-requests/2.32.3	5	0.5	1
1434	55	password	success	2025-05-05 17:51:40.798198	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	0	0.5	1
1497	62	password	success	2025-05-08 13:57:18.80771	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1498	62	totp	success	2025-05-08 13:57:47.414793	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1499	62	webauthn	success	2025-05-08 13:57:54.894715	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1512	54	password	success	2025-05-11 11:39:35.238699	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1513	54	totp	success	2025-05-11 11:39:47.058915	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1514	54	webauthn	success	2025-05-11 11:39:52.174121	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1554	22	password	success	2025-05-12 09:56:15.64605	192.168.2.116	Unknown	Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0	0	0.5	1
1555	22	totp	failed	2025-05-12 09:56:32.866571	192.168.2.116	Unknown	Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0	1	0.5	1
1556	22	totp	success	2025-05-12 09:56:43.561536	192.168.2.116	Unknown	Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0	0	0.5	1
1557	22	password	success	2025-05-12 09:58:57.747766	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1558	22	totp	success	2025-05-12 09:59:12.380054	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1559	22	webauthn	success	2025-05-12 09:59:17.542856	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1288	69	password	failed	2025-04-30 19:13:59.122479	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	2	0.5	1
1290	69	totp	success	2025-04-30 19:15:07.605948	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1291	69	webauthn	success	2025-04-30 19:19:58.680937	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1320	22	password	success	2025-05-02 13:43:28.561862	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1322	22	webauthn	success	2025-05-02 13:43:58.329551	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1367	54	password	success	2025-05-03 23:36:24.885002	192.168.60.3	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1369	54	webauthn	success	2025-05-03 23:37:48.952415	192.168.60.3	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1377	56	password	failed	2025-05-04 00:22:31.210694	192.168.60.3	Unknown	python-requests/2.32.3	4	0.5	1
1435	55	totp	success	2025-05-05 17:53:42.300001	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	0	0.5	1
1436	55	webauthn	success	2025-05-05 17:53:48.420245	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	0	0.5	1
1437	22	password	success	2025-05-05 18:22:56.782503	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	0	0.5	1
1441	22	totp	success	2025-05-05 18:39:07.655545	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	0	0.5	1
1442	22	webauthn	success	2025-05-05 18:39:12.782355	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	0	0.5	1
1443	22	password	success	2025-05-05 19:13:35.213527	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	0	0.5	1
1515	54	password	success	2025-05-11 11:56:54.788854	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1516	54	totp	success	2025-05-11 11:57:08.51554	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1517	54	webauthn	success	2025-05-11 11:57:14.837275	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1560	57	password	success	2025-05-12 10:00:41.771143	127.0.0.1	Unknown	IAMaaS API Access	0	0.5	2
1569	54	password	success	2025-05-12 16:31:55.220812	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1570	54	totp	success	2025-05-12 16:32:12.707231	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1571	54	webauthn	success	2025-05-12 16:32:39.515082	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1573	54	totp	success	2025-05-12 16:34:49.882429	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	0	0.5	1
1596	54	password	success	2025-05-13 10:37:42.715478	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1597	54	totp	failed	2025-05-13 10:38:08.668283	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	1	0.5	1
1598	54	totp	success	2025-05-13 10:38:26.972874	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1599	54	webauthn	success	2025-05-13 10:39:02.172837	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1600	54	password	success	2025-05-13 15:27:52.849447	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1601	54	totp	success	2025-05-13 15:28:44.671267	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1602	54	webauthn	success	2025-05-13 15:29:06.317054	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1603	22	password	success	2025-05-13 17:11:39.858331	192.168.2.116	Unknown	Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0	0	0.5	1
1604	22	totp	failed	2025-05-13 17:11:59.988406	192.168.2.116	Unknown	Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0	1	0.5	1
1605	22	totp	success	2025-05-13 17:12:11.008457	192.168.2.116	Unknown	Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0	0	0.5	1
1289	69	password	success	2025-04-30 19:14:05.154424	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1321	22	totp	success	2025-05-02 13:43:52.302085	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1438	22	totp	success	2025-05-05 18:23:15.323117	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	0	0.5	1
1439	22	webauthn	success	2025-05-05 18:23:20.495671	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	0	0.5	1
1440	22	password	success	2025-05-05 18:38:49.038893	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	0	0.5	1
1444	22	totp	success	2025-05-05 19:13:48.440427	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	0	0.5	1
1445	22	webauthn	success	2025-05-05 19:13:53.763074	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	0	0.5	1
1446	69	password	failed	2025-05-05 20:11:05.462354	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	1	0.5	1
1518	54	password	success	2025-05-11 12:13:06.996238	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1519	54	totp	success	2025-05-11 12:13:17.218252	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1520	54	webauthn	success	2025-05-11 12:13:21.410161	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1561	55	password	success	2025-05-12 10:43:56.749497	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	0	0.5	1
1562	55	totp	success	2025-05-12 10:44:12.597628	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	0	0.5	1
1563	55	webauthn	success	2025-05-12 10:44:19.064307	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	0	0.5	1
1565	57	password	success	2025-05-12 10:57:59.123316	127.0.0.1	Unknown	IAMaaS API Access	0	0.5	2
1566	54	password	success	2025-05-12 11:05:29.122436	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	0	0.5	1
1572	54	password	success	2025-05-12 16:34:39.717144	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	0	0.5	1
1574	54	webauthn	success	2025-05-12 16:34:55.167489	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	0	0.5	1
460	22	password	success	2025-04-14 10:12:25.921903	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
462	22	totp	success	2025-04-14 10:12:49.558407	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
463	22	webauthn	success	2025-04-14 10:12:54.065754	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1521	54	password	failed	2025-05-11 12:29:19.170704	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	1	0.5	1
1522	54	password	success	2025-05-11 12:29:26.328357	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1523	54	totp	success	2025-05-11 12:29:36.917486	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1524	54	webauthn	success	2025-05-11 12:29:41.396507	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1564	57	password	success	2025-05-12 10:57:07.584538	127.0.0.1	Unknown	IAMaaS API Access	0	0.5	2
1567	54	totp	success	2025-05-12 11:05:44.221057	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	0	0.5	1
1568	54	webauthn	success	2025-05-12 11:05:48.840216	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	0	0.5	1
1575	54	password	success	2025-05-12 17:03:51.202612	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	0	0.5	1
1576	54	totp	success	2025-05-12 17:04:13.658154	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	0	0.5	1
1577	54	webauthn	success	2025-05-12 17:04:18.197647	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	0	0.5	1
1578	54	password	success	2025-05-12 17:11:20.581674	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1580	54	webauthn	success	2025-05-12 17:11:46.159982	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1581	70	password	success	2025-05-12 17:16:54.056223	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	0	0.5	1
1583	70	password	success	2025-05-12 17:18:38.655479	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1587	54	totp	success	2025-05-12 17:23:09.279079	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1591	22	totp	success	2025-05-12 17:49:42.568382	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1594	55	totp	success	2025-05-12 19:19:07.043579	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	0	0.5	1
1525	54	password	success	2025-05-11 12:51:12.478009	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1526	54	totp	success	2025-05-11 12:51:24.338612	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1527	54	webauthn	success	2025-05-11 12:51:28.275895	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1528	22	password	success	2025-05-11 15:04:28.30391	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1530	22	webauthn	success	2025-05-11 15:04:53.911601	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1579	54	totp	success	2025-05-12 17:11:37.872357	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1586	54	password	success	2025-05-12 17:22:52.532534	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1588	54	webauthn	success	2025-05-12 17:23:14.640451	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1590	22	password	success	2025-05-12 17:48:40.255319	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1592	22	webauthn	success	2025-05-12 17:49:47.761251	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1593	55	password	success	2025-05-12 19:18:36.464306	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	0	0.5	1
1595	55	webauthn	success	2025-05-12 19:19:11.427259	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	0	0.5	1
1529	22	totp	success	2025-05-11 15:04:48.362333	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1582	70	totp	success	2025-05-12 17:17:35.713534	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0	0	0.5	1
503	57	webauthn	failed	2025-04-14 16:33:36.173672	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	1	0.5	1
1531	22	password	success	2025-05-11 15:32:44.803371	192.168.60.3	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1533	22	webauthn	success	2025-05-11 15:33:29.591033	192.168.60.3	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1539	56	password	failed	2025-05-11 16:16:22.025014	192.168.60.3	Unknown	python-requests/2.32.3	3	0.5	1
1584	70	totp	success	2025-05-12 17:18:55.281616	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1532	22	totp	success	2025-05-11 15:33:06.508449	192.168.60.3	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1534	22	password	success	2025-05-11 16:10:24.487453	192.168.60.3	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1536	22	webauthn	success	2025-05-11 16:10:42.547175	192.168.60.3	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1540	56	password	failed	2025-05-11 16:16:22.435711	192.168.60.3	Unknown	python-requests/2.32.3	4	0.5	1
1585	70	webauthn	success	2025-05-12 17:19:41.032789	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1589	57	password	success	2025-05-12 17:38:01.153227	127.0.0.1	Unknown	IAMaaS API Access	0	0.5	2
1535	22	totp	success	2025-05-11 16:10:38.8721	192.168.60.3	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1541	56	password	failed	2025-05-11 16:16:22.850821	192.168.60.3	Unknown	python-requests/2.32.3	5	0.5	1
1542	22	password	success	2025-05-11 16:21:01.922706	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1544	22	webauthn	success	2025-05-11 16:21:31.420227	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1537	56	password	failed	2025-05-11 16:16:21.22068	192.168.60.3	Unknown	python-requests/2.32.3	1	0.5	1
1543	22	totp	success	2025-05-11 16:21:24.890748	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36	0	0.5	1
1538	56	password	failed	2025-05-11 16:16:21.633668	192.168.60.3	Unknown	python-requests/2.32.3	2	0.5	1
822	22	webauthn	success	2025-04-16 09:43:18.79819	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
824	57	totp	success	2025-04-16 09:47:42.121321	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
825	22	password	success	2025-04-16 09:48:17.233123	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
827	22	totp	success	2025-04-16 09:48:42.466765	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
828	22	webauthn	success	2025-04-16 09:48:47.456798	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
868	59	totp	success	2025-04-16 15:52:28.038691	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
869	59	webauthn	success	2025-04-16 15:52:32.938158	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
910	58	password	failed	2025-04-17 16:05:42.02635	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	3	0.5	1
914	54	totp	success	2025-04-17 16:10:15.44579	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
916	57	totp	failed	2025-04-17 16:10:58.355068	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	1	0.5	1
929	57	password	failed	2025-04-17 16:47:04.212631	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	5	0.5	1
911	58	password	failed	2025-04-17 16:05:45.485927	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	4	0.5	1
917	57	totp	failed	2025-04-17 16:11:07.992938	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	2	0.5	1
926	57	password	failed	2025-04-17 16:46:55.140006	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	2	0.5	1
930	22	password	failed	2025-04-17 16:47:55.213324	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	1	0.5	1
912	58	password	failed	2025-04-17 16:05:46.904378	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	5	0.5	1
918	22	password	success	2025-04-17 16:12:22.796751	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
925	57	password	failed	2025-04-17 16:46:51.479481	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	1	0.5	1
913	54	password	success	2025-04-17 16:09:47.687975	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
915	57	password	success	2025-04-17 16:10:43.03642	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
920	22	totp	success	2025-04-17 16:13:47.82546	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
923	22	totp	success	2025-04-17 16:44:43.439415	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
928	57	password	failed	2025-04-17 16:47:01.994128	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	4	0.5	1
932	22	totp	success	2025-04-17 16:48:14.546764	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1007	56	password	success	2025-04-21 20:50:27.708143	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1169	54	totp	success	2025-04-25 20:43:13.157862	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1172	54	password	success	2025-04-25 21:00:30.80121	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1174	54	webauthn	success	2025-04-25 21:00:56.650782	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1170	54	webauthn	success	2025-04-25 20:43:18.052028	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1171	54	password	failed	2025-04-25 21:00:20.970696	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	3	0.5	1
1	55	password	success	2025-04-07 15:08:13.849693	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
2	55	totp	success	2025-04-07 15:08:37.02091	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
3	55	password	failed	2025-04-07 15:09:00.94601	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	1	0.5	1
4	55	password	failed	2025-04-07 15:09:08.679228	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	2	0.5	1
5	55	password	failed	2025-04-07 15:09:10.225275	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	3	0.5	1
6	55	password	failed	2025-04-07 15:09:15.138944	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	4	0.5	1
7	55	password	failed	2025-04-07 15:09:18.962248	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	5	0.5	1
8	22	password	success	2025-04-07 15:09:58.826699	192.168.2.110	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
9	22	totp	failed	2025-04-07 15:10:30.565004	192.168.2.110	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	1	0.5	1
10	22	totp	success	2025-04-07 15:10:40.913858	192.168.2.110	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
11	56	password	success	2025-04-07 15:18:48.000766	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
12	56	totp	failed	2025-04-07 15:19:18.212323	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	1	0.5	1
13	56	totp	failed	2025-04-07 15:19:20.678582	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	2	0.5	1
14	56	totp	failed	2025-04-07 15:19:22.365347	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	3	0.5	1
15	56	totp	failed	2025-04-07 15:19:24.526708	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	4	0.5	1
16	56	totp	failed	2025-04-07 15:19:27.737537	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	5	0.5	1
17	56	password	success	2025-04-07 15:27:30.103613	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
18	22	password	success	2025-04-07 15:28:22.773018	192.168.2.110	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
19	22	totp	success	2025-04-07 15:28:36.534143	192.168.2.110	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
20	56	password	success	2025-04-07 15:32:09.666155	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
21	56	password	success	2025-04-07 16:14:34.57997	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
22	56	totp	success	2025-04-07 16:16:11.516601	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
23	22	password	failed	2025-04-07 16:16:33.858043	192.168.2.110	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	1	0.5	1
24	22	password	success	2025-04-07 16:16:40.127059	192.168.2.110	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
25	22	totp	success	2025-04-07 16:16:55.904616	192.168.2.110	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
26	22	password	success	2025-04-07 16:40:42.983428	192.168.2.110	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
27	22	totp	success	2025-04-07 16:40:57.532275	192.168.2.110	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
28	55	password	success	2025-04-07 16:55:03.777362	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
29	55	totp	failed	2025-04-07 16:55:37.902416	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	1	0.5	1
30	55	totp	success	2025-04-07 16:55:46.305881	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
31	22	password	success	2025-04-07 16:56:43.694171	192.168.2.110	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
32	22	totp	failed	2025-04-07 16:57:03.05827	192.168.2.110	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	2	0.5	1
33	22	totp	success	2025-04-07 16:57:15.112854	192.168.2.110	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
34	54	password	success	2025-04-07 17:05:50.308185	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
35	54	totp	success	2025-04-07 17:06:15.576219	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
36	22	password	success	2025-04-07 17:17:03.120319	192.168.2.110	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
37	22	totp	success	2025-04-07 17:17:13.350831	192.168.2.110	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
38	22	password	success	2025-04-07 17:39:26.727639	192.168.2.110	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
39	22	totp	success	2025-04-07 17:39:44.898983	192.168.2.110	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
40	55	password	success	2025-04-07 17:40:41.243496	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
41	55	totp	failed	2025-04-07 17:40:48.561662	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	2	0.5	1
42	55	totp	failed	2025-04-07 17:40:51.573779	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	3	0.5	1
43	55	totp	failed	2025-04-07 17:40:54.050797	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	4	0.5	1
44	55	totp	failed	2025-04-07 17:40:55.701801	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	5	0.5	1
45	55	totp	success	2025-04-07 17:43:15.882136	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
46	55	password	failed	2025-04-07 17:51:59.846655	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	6	0.5	1
47	22	password	success	2025-04-07 17:58:19.259707	192.168.2.110	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
48	22	totp	success	2025-04-07 17:58:42.088785	192.168.2.110	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
49	55	password	success	2025-04-07 18:12:37.714783	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
50	55	totp	failed	2025-04-07 18:12:52.422572	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	6	0.5	1
51	22	password	success	2025-04-07 18:14:00.033307	192.168.2.110	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
52	22	totp	success	2025-04-07 18:14:25.490345	192.168.2.110	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
53	55	totp	failed	2025-04-07 18:18:48.818016	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	7	0.5	1
54	22	password	success	2025-04-07 19:04:20.504915	192.168.2.110	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
55	22	totp	success	2025-04-07 19:04:40.476137	192.168.2.110	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
56	56	password	failed	2025-04-07 19:06:08.855544	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	1	0.5	1
57	56	password	failed	2025-04-07 19:06:11.654158	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	2	0.5	1
58	56	password	failed	2025-04-07 19:06:12.795141	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	3	0.5	1
59	56	password	failed	2025-04-07 19:06:14.116149	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	4	0.5	1
60	56	password	failed	2025-04-07 19:06:15.163903	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	5	0.5	1
61	55	password	success	2025-04-07 19:08:01.312352	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
62	55	totp	success	2025-04-07 19:08:21.161186	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
63	22	password	success	2025-04-07 19:24:35.680676	192.168.2.110	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
64	22	totp	success	2025-04-07 19:24:48.877064	192.168.2.110	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
65	55	password	success	2025-04-07 19:40:23.860978	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
66	55	totp	success	2025-04-07 19:40:41.770752	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
67	22	password	success	2025-04-07 19:42:36.713666	192.168.2.110	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
68	22	totp	success	2025-04-07 19:42:47.36903	192.168.2.110	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
69	55	password	failed	2025-04-07 19:44:34.041945	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	7	0.5	1
70	54	password	success	2025-04-07 19:46:08.653541	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
71	54	totp	success	2025-04-07 19:46:39.159522	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
72	55	password	success	2025-04-07 20:02:24.894681	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
73	55	totp	success	2025-04-07 20:02:43.395179	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
74	22	password	success	2025-04-07 20:04:03.543245	192.168.2.110	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
75	22	totp	success	2025-04-07 20:04:21.779766	192.168.2.110	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
76	22	password	success	2025-04-08 11:13:11.392877	192.168.2.110	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
77	22	totp	failed	2025-04-08 11:13:29.936268	192.168.2.110	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	1	0.5	1
78	22	totp	success	2025-04-08 11:13:45.238607	192.168.2.110	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
79	54	password	success	2025-04-08 11:24:42.550598	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
80	54	totp	success	2025-04-08 11:24:57.229269	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
81	22	password	success	2025-04-08 11:29:37.169541	192.168.2.110	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
82	22	totp	success	2025-04-08 11:29:53.540799	192.168.2.110	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
83	55	password	success	2025-04-08 11:42:29.551532	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
84	55	totp	success	2025-04-08 11:42:41.493409	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
85	54	password	success	2025-04-08 11:47:59.908019	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
86	54	totp	success	2025-04-08 11:48:14.782073	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
87	56	password	success	2025-04-08 11:49:12.633004	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
88	56	totp	success	2025-04-08 11:49:24.157622	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
89	22	password	success	2025-04-08 11:50:08.271537	192.168.2.110	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
90	22	totp	success	2025-04-08 11:50:28.477764	192.168.2.110	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
91	54	password	success	2025-04-08 11:58:19.325922	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
92	54	totp	success	2025-04-08 11:58:37.505592	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
93	56	password	success	2025-04-08 12:13:31.792979	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
94	56	totp	success	2025-04-08 12:13:43.822315	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
95	22	password	success	2025-04-08 12:14:40.000304	192.168.2.110	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
96	22	totp	success	2025-04-08 12:14:48.298636	192.168.2.110	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
97	54	password	success	2025-04-08 12:15:13.370294	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
98	54	totp	success	2025-04-08 12:15:29.076649	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
99	55	password	success	2025-04-08 15:13:56.205492	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
100	55	totp	failed	2025-04-08 15:14:14.046882	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	1	0.5	1
101	55	totp	success	2025-04-08 15:14:25.697651	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
102	54	password	success	2025-04-08 15:16:10.276207	192.168.2.110	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
103	54	totp	success	2025-04-08 15:16:20.313285	192.168.2.110	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
104	22	password	success	2025-04-08 15:18:31.859899	192.168.2.110	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
105	22	totp	success	2025-04-08 15:19:11.103207	192.168.2.110	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
106	54	password	success	2025-04-08 15:24:36.520612	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
107	54	totp	success	2025-04-08 15:25:28.759098	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
108	22	password	success	2025-04-08 15:37:20.309547	192.168.2.110	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
109	22	totp	success	2025-04-08 15:37:41.121869	192.168.2.110	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
110	54	password	success	2025-04-08 15:53:19.323179	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
111	54	totp	success	2025-04-08 15:53:36.426821	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
112	54	password	success	2025-04-08 16:09:43.952499	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
113	54	totp	success	2025-04-08 16:09:56.281911	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
114	22	password	success	2025-04-08 16:11:44.913969	192.168.2.110	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
115	22	totp	failed	2025-04-08 16:12:01.208263	192.168.2.110	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	2	0.5	1
116	22	totp	success	2025-04-08 16:12:09.12621	192.168.2.110	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
117	54	password	success	2025-04-08 17:17:08.969573	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
118	54	totp	success	2025-04-08 17:20:08.298563	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
119	54	password	success	2025-04-08 17:43:22.459544	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
120	54	totp	success	2025-04-08 17:43:38.901342	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
121	54	password	success	2025-04-08 18:00:35.396356	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
122	54	totp	success	2025-04-08 18:01:45.175585	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
123	56	password	success	2025-04-08 18:03:54.395865	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
124	56	totp	success	2025-04-08 18:04:17.181226	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
125	22	password	success	2025-04-08 18:04:47.444036	192.168.2.110	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
126	22	totp	success	2025-04-08 18:05:05.756059	192.168.2.110	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
127	54	password	success	2025-04-08 18:06:45.00126	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
128	54	totp	failed	2025-04-08 18:07:06.083104	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	1	0.5	1
129	54	totp	failed	2025-04-08 18:07:22.981897	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	2	0.5	1
130	54	totp	success	2025-04-08 18:07:44.30516	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
131	54	password	success	2025-04-08 18:24:38.436151	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
132	54	totp	success	2025-04-08 18:24:51.387097	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
133	22	password	success	2025-04-08 18:26:36.650897	192.168.2.110	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
134	22	totp	success	2025-04-08 18:26:57.66647	192.168.2.110	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
135	54	password	success	2025-04-08 18:43:39.010756	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
136	54	totp	success	2025-04-08 18:43:48.246465	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
137	22	password	success	2025-04-08 18:59:38.471616	192.168.2.110	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
138	22	totp	success	2025-04-08 19:00:07.195915	192.168.2.110	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
139	54	password	success	2025-04-08 19:01:05.931436	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
140	54	totp	success	2025-04-08 19:01:15.65929	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
141	54	password	success	2025-04-08 19:17:22.140365	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
142	54	totp	success	2025-04-08 19:17:37.464592	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
143	22	password	success	2025-04-08 19:20:21.760644	192.168.2.110	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
144	22	totp	success	2025-04-08 19:20:40.483225	192.168.2.110	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
145	54	password	success	2025-04-08 19:32:45.83337	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
146	54	totp	success	2025-04-08 19:32:58.20039	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
147	22	password	success	2025-04-08 19:51:30.151341	192.168.2.110	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
148	22	totp	success	2025-04-08 19:51:48.246551	192.168.2.110	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
149	22	password	failed	2025-04-08 20:07:57.064655	192.168.2.110	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	1	0.5	1
150	22	password	success	2025-04-08 20:08:05.569615	192.168.2.110	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
151	22	totp	success	2025-04-08 20:08:12.513774	192.168.2.110	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
152	56	password	success	2025-04-08 20:11:05.936644	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
153	56	totp	success	2025-04-08 20:11:22.925314	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
154	22	password	success	2025-04-09 15:42:09.025261	192.168.2.110	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
155	22	totp	failed	2025-04-09 15:42:28.932063	192.168.2.110	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	1	0.5	1
156	22	totp	success	2025-04-09 15:42:42.10399	192.168.2.110	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
157	22	password	success	2025-04-09 16:05:29.077114	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
158	22	totp	success	2025-04-09 16:06:12.579909	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
159	55	password	success	2025-04-09 16:08:21.529171	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
160	55	totp	success	2025-04-09 16:10:23.425944	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
161	54	password	success	2025-04-09 16:12:49.998357	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
162	54	totp	success	2025-04-09 16:13:38.109728	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
163	22	password	success	2025-04-10 15:11:27.278159	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
164	22	totp	success	2025-04-10 15:11:48.110254	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
165	22	password	success	2025-04-11 09:49:20.237765	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
166	22	totp	success	2025-04-11 09:49:36.804561	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
167	55	password	success	2025-04-11 09:52:35.205095	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
168	55	totp	success	2025-04-11 09:52:48.791454	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
169	56	password	success	2025-04-11 09:55:10.869665	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
170	56	totp	success	2025-04-11 09:55:21.628093	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
171	22	password	failed	2025-04-11 10:08:20.827469	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	1	0.5	1
172	22	password	success	2025-04-11 10:08:26.524314	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
173	22	totp	success	2025-04-11 10:08:46.5827	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
174	56	password	success	2025-04-11 10:09:14.017276	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
175	55	password	success	2025-04-11 10:09:28.261588	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
176	55	totp	success	2025-04-11 10:09:40.154454	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
177	22	password	success	2025-04-11 10:25:11.10572	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
178	22	totp	success	2025-04-11 10:25:19.470823	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
179	55	password	success	2025-04-11 10:36:43.402445	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
180	55	totp	success	2025-04-11 10:36:53.988616	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
181	22	password	success	2025-04-11 10:41:35.483365	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
182	22	totp	success	2025-04-11 10:41:53.371953	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
183	22	password	success	2025-04-11 10:47:27.783313	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
184	22	totp	success	2025-04-11 10:47:45.067382	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
185	56	password	success	2025-04-11 10:48:13.73739	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
186	56	totp	success	2025-04-11 10:48:23.818135	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
187	54	password	success	2025-04-11 10:58:26.075546	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
188	54	totp	success	2025-04-11 10:58:45.023297	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
189	56	password	success	2025-04-11 11:05:28.623909	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
190	56	totp	success	2025-04-11 11:05:37.612061	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
191	54	password	success	2025-04-11 11:14:07.291025	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
192	54	totp	success	2025-04-11 11:14:16.652299	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
193	22	password	success	2025-04-11 11:15:58.360024	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
194	22	totp	success	2025-04-11 11:16:16.385961	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
195	56	password	success	2025-04-11 11:21:33.818859	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
196	56	totp	success	2025-04-11 11:21:46.369563	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
197	54	password	success	2025-04-11 11:29:22.016082	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
198	54	totp	success	2025-04-11 11:29:38.562196	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
199	22	password	success	2025-04-11 14:52:27.78709	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
200	22	totp	success	2025-04-11 14:52:52.107622	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
201	22	password	success	2025-04-11 14:55:25.5046	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
202	22	totp	success	2025-04-11 14:55:43.096809	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
203	22	password	success	2025-04-11 15:04:07.883025	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
204	22	totp	success	2025-04-11 15:04:23.103834	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
205	56	password	success	2025-04-11 15:05:16.533892	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
206	56	totp	success	2025-04-11 15:05:36.102254	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
207	56	password	success	2025-04-11 15:16:58.567482	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
208	56	totp	success	2025-04-11 15:17:12.717685	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
209	22	password	success	2025-04-11 15:17:51.86477	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
210	22	totp	success	2025-04-11 15:18:06.857515	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
211	22	password	success	2025-04-11 15:24:22.76152	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
212	22	totp	success	2025-04-11 15:24:39.439268	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
213	56	password	success	2025-04-11 15:25:22.17475	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
214	56	totp	success	2025-04-11 15:25:36.471374	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
215	56	password	success	2025-04-11 15:44:07.182015	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
217	55	password	success	2025-04-11 15:45:56.502411	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
218	55	totp	success	2025-04-11 15:46:06.797429	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
219	55	password	success	2025-04-11 15:46:24.878095	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
220	55	totp	success	2025-04-11 15:46:41.412824	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
221	56	password	success	2025-04-11 15:50:29.492301	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
222	56	totp	failed	2025-04-11 15:50:40.582951	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	1	0.5	1
223	56	totp	success	2025-04-11 15:50:52.716057	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
224	56	totp	failed	2025-04-11 15:52:21.76408	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	2	0.5	1
225	56	totp	success	2025-04-11 15:52:41.821365	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
226	56	totp	success	2025-04-11 15:53:07.476682	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
227	56	password	success	2025-04-11 16:15:06.578413	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
228	56	totp	success	2025-04-11 16:15:17.124379	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
229	56	totp	success	2025-04-11 16:26:40.10166	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
230	56	password	success	2025-04-11 16:37:40.54961	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
231	56	totp	success	2025-04-11 16:37:56.052509	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
232	56	password	success	2025-04-11 17:02:27.33702	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
233	56	totp	success	2025-04-11 17:02:39.010888	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
234	56	password	success	2025-04-11 17:23:11.77523	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
235	56	totp	success	2025-04-11 17:23:26.6146	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
236	56	totp	failed	2025-04-11 17:26:24.759975	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	3	0.5	1
237	56	totp	success	2025-04-11 17:26:48.13974	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
238	56	password	success	2025-04-11 17:29:11.638428	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
239	56	totp	success	2025-04-11 17:29:20.151059	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
240	56	totp	success	2025-04-11 17:33:38.055125	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
241	56	password	success	2025-04-11 17:37:51.062925	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
242	56	totp	success	2025-04-11 17:38:06.892086	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
243	56	password	success	2025-04-11 17:41:54.665998	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
244	56	totp	success	2025-04-11 17:42:06.273504	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
245	56	password	success	2025-04-11 17:55:56.106359	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
246	56	totp	success	2025-04-11 17:56:12.805662	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
247	22	password	success	2025-04-11 18:03:10.925372	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
248	22	totp	success	2025-04-11 18:03:28.710444	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
249	22	password	failed	2025-04-11 18:18:57.205323	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	2	0.5	1
250	22	password	success	2025-04-11 18:19:23.368775	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
251	22	totp	success	2025-04-11 18:19:39.231685	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
252	56	password	success	2025-04-11 18:52:50.549502	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
253	56	totp	success	2025-04-11 18:53:08.350984	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
254	22	password	success	2025-04-11 18:59:32.94869	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
255	22	totp	success	2025-04-11 18:59:41.238142	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
256	22	password	success	2025-04-11 19:24:17.542219	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
257	22	totp	success	2025-04-11 19:24:39.700819	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
258	22	password	success	2025-04-11 19:31:45.023663	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
259	22	totp	failed	2025-04-11 19:32:00.065976	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	1	0.5	1
260	22	totp	success	2025-04-11 19:32:09.972302	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
261	22	totp	success	2025-04-11 19:41:52.398429	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
262	22	password	success	2025-04-11 19:52:04.709482	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
263	22	totp	success	2025-04-11 19:52:18.881645	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
264	55	password	success	2025-04-11 19:59:54.292135	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
265	55	totp	success	2025-04-11 20:00:09.286341	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
266	56	password	success	2025-04-11 20:17:03.21634	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
267	56	totp	success	2025-04-11 20:17:14.755369	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
268	55	password	success	2025-04-11 20:24:56.121677	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
269	55	totp	success	2025-04-11 20:25:10.126594	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
270	56	password	success	2025-04-11 20:40:42.904635	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
271	56	totp	success	2025-04-11 20:40:55.835043	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
272	55	password	success	2025-04-11 20:50:30.831257	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
273	55	totp	success	2025-04-11 20:50:48.353485	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
274	56	password	success	2025-04-11 20:59:05.483608	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
275	56	totp	success	2025-04-11 20:59:17.778522	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
276	22	password	success	2025-04-11 21:39:37.11835	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
277	22	totp	success	2025-04-11 21:40:08.459071	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
278	22	totp	success	2025-04-11 21:42:16.22821	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
279	22	password	success	2025-04-11 22:13:24.189407	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
280	22	totp	success	2025-04-11 22:13:44.130302	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
281	22	totp	success	2025-04-11 22:17:27.621173	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
282	56	password	success	2025-04-11 22:32:36.063137	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
283	56	totp	success	2025-04-11 22:32:47.184018	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
284	56	totp	success	2025-04-11 22:33:23.563879	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
285	56	totp	success	2025-04-11 22:41:18.654602	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
286	56	totp	success	2025-04-11 22:41:55.282518	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
287	54	password	success	2025-04-11 22:42:37.380669	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
288	54	totp	success	2025-04-11 22:42:49.451214	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
289	54	password	success	2025-04-11 22:50:32.979024	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
290	54	totp	success	2025-04-11 22:50:46.813871	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
291	54	password	success	2025-04-11 22:51:55.083465	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
292	54	totp	success	2025-04-11 22:52:10.337005	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
293	54	password	success	2025-04-11 22:54:57.406474	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
294	54	totp	failed	2025-04-11 22:55:11.224878	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	1	0.5	1
295	54	totp	success	2025-04-11 22:55:26.169432	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
296	54	password	success	2025-04-11 22:58:29.589213	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
297	54	totp	success	2025-04-11 22:58:43.914808	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
298	54	password	success	2025-04-11 23:00:05.975482	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
299	54	totp	success	2025-04-11 23:00:16.498169	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
300	54	password	success	2025-04-11 23:32:31.180473	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
301	54	totp	success	2025-04-11 23:32:49.789632	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
302	54	totp	failed	2025-04-11 23:37:56.348458	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	2	0.5	1
303	54	totp	success	2025-04-11 23:38:09.646652	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
304	54	password	success	2025-04-11 23:38:54.966987	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
305	54	totp	success	2025-04-11 23:39:06.898806	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
306	54	password	success	2025-04-11 23:51:14.129456	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
307	54	totp	success	2025-04-11 23:51:24.93196	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
308	54	totp	success	2025-04-11 23:57:16.197404	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
309	56	password	success	2025-04-12 11:04:41.187456	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
310	56	totp	failed	2025-04-12 11:05:07.235388	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	1	0.5	1
311	56	totp	success	2025-04-12 11:05:23.610525	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
312	22	password	success	2025-04-12 11:14:48.379431	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
313	22	totp	success	2025-04-12 11:15:17.306351	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
314	22	password	success	2025-04-12 11:23:04.537549	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
315	22	totp	success	2025-04-12 11:23:29.232393	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
316	22	password	failed	2025-04-12 12:14:55.172103	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	1	0.5	1
317	22	password	failed	2025-04-12 12:15:02.63317	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	2	0.5	1
318	22	password	success	2025-04-12 12:16:25.54622	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
319	22	totp	success	2025-04-12 12:16:37.358193	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
320	22	password	success	2025-04-12 12:31:41.462854	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
321	22	totp	success	2025-04-12 12:31:58.623986	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
322	22	totp	success	2025-04-12 12:45:36.75765	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
323	22	password	success	2025-04-12 12:48:58.547566	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
324	22	totp	success	2025-04-12 12:49:08.113715	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
325	22	totp	failed	2025-04-12 12:53:30.620883	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	1	0.5	1
326	22	totp	success	2025-04-12 12:53:39.814939	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
327	22	password	success	2025-04-12 13:05:49.254733	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
328	22	totp	success	2025-04-12 13:05:58.224224	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
329	22	password	success	2025-04-12 13:22:32.101859	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
330	22	totp	success	2025-04-12 13:22:38.882795	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
331	56	password	success	2025-04-12 13:26:05.814125	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
332	56	totp	success	2025-04-12 13:26:18.524316	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
333	56	totp	failed	2025-04-12 13:26:45.779705	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	2	0.5	1
335	55	password	failed	2025-04-12 13:27:44.569337	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	1	0.5	1
337	55	totp	success	2025-04-12 13:27:59.425161	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
339	54	totp	failed	2025-04-12 13:30:06.687068	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	1	0.5	1
341	56	password	failed	2025-04-12 13:40:22.248982	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	1	0.5	1
343	56	totp	success	2025-04-12 13:40:45.899166	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
344	56	totp	success	2025-04-12 13:40:58.807409	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
345	56	totp	failed	2025-04-12 13:41:18.460733	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	3	0.5	1
346	56	totp	failed	2025-04-12 13:41:20.886284	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	4	0.5	1
347	56	totp	failed	2025-04-12 13:41:23.272473	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	5	0.5	1
348	55	password	success	2025-04-12 13:42:01.465695	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
349	55	totp	success	2025-04-12 13:42:09.643956	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
350	22	password	success	2025-04-12 13:43:45.65044	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
351	22	totp	success	2025-04-12 13:44:10.954748	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
352	56	password	success	2025-04-12 13:55:35.063806	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
353	56	totp	success	2025-04-12 13:55:50.261788	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
354	55	password	success	2025-04-12 13:56:18.625067	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
355	55	totp	failed	2025-04-12 13:56:30.098601	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	1	0.5	1
356	55	totp	success	2025-04-12 13:56:40.247206	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
357	22	password	success	2025-04-12 14:32:18.331207	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
358	22	totp	success	2025-04-12 14:32:37.276909	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
359	57	password	success	2025-04-12 14:35:05.872695	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
360	57	totp	success	2025-04-12 14:35:52.781476	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
361	57	totp	success	2025-04-12 14:49:15.180568	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
362	57	password	success	2025-04-12 15:07:25.339685	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
363	57	totp	success	2025-04-12 15:07:39.802914	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
364	54	password	success	2025-04-12 15:10:35.78963	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
365	54	totp	success	2025-04-12 15:10:49.127782	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
366	57	totp	success	2025-04-12 15:14:08.640453	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
367	22	password	success	2025-04-12 15:26:20.868745	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
368	22	totp	success	2025-04-12 15:26:45.95245	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
369	22	password	success	2025-04-12 15:32:42.415661	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
370	22	totp	success	2025-04-12 15:33:07.776887	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
371	57	password	success	2025-04-12 15:53:02.831105	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
372	57	totp	success	2025-04-12 15:53:13.997707	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
373	57	totp	success	2025-04-12 15:55:29.041774	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
374	57	password	success	2025-04-12 16:02:47.78522	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
375	57	totp	success	2025-04-12 16:02:59.241517	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
376	57	password	success	2025-04-12 16:20:17.035882	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
377	57	totp	success	2025-04-12 16:20:37.88964	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
378	57	totp	success	2025-04-12 16:31:57.092511	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
379	57	password	success	2025-04-12 16:36:02.813078	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
380	57	totp	success	2025-04-12 16:36:14.234385	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
381	57	password	success	2025-04-12 17:01:11.971466	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
382	57	totp	success	2025-04-12 17:01:24.400111	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
383	57	password	success	2025-04-12 17:34:08.345489	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
384	57	totp	success	2025-04-12 17:34:25.775471	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
385	57	webauthn	success	2025-04-12 17:35:27.560244	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
386	22	password	success	2025-04-12 17:35:46.825056	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
387	22	totp	success	2025-04-12 17:36:06.633704	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
388	22	webauthn	success	2025-04-12 17:36:10.791324	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
389	57	password	success	2025-04-12 17:46:30.632073	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
390	57	totp	success	2025-04-12 17:46:45.554117	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
391	57	webauthn	success	2025-04-12 17:46:53.44192	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
392	55	password	success	2025-04-12 17:47:07.65295	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
393	55	totp	success	2025-04-12 17:47:22.932395	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
394	55	webauthn	success	2025-04-12 17:47:29.171737	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
395	22	password	failed	2025-04-12 17:47:48.610023	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	3	0.5	1
396	22	password	success	2025-04-12 17:47:55.472934	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
397	22	totp	success	2025-04-12 17:48:10.696528	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
398	22	webauthn	success	2025-04-12 17:48:14.936223	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
399	54	password	success	2025-04-12 17:52:14.298716	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
400	54	totp	success	2025-04-12 17:52:26.858415	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
401	54	webauthn	success	2025-04-12 17:52:30.790558	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
402	22	password	success	2025-04-12 17:53:12.7167	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
403	22	totp	success	2025-04-12 17:53:21.773089	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
404	22	webauthn	success	2025-04-12 17:53:25.319502	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
405	56	password	success	2025-04-12 18:09:45.789202	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
406	56	totp	success	2025-04-12 18:10:06.390099	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
407	56	webauthn	failed	2025-04-12 18:10:12.575506	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	1	0.5	1
408	56	webauthn	success	2025-04-12 18:14:32.712413	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
409	57	password	success	2025-04-12 18:32:16.122133	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
410	57	totp	success	2025-04-12 18:32:28.204927	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
411	57	webauthn	failed	2025-04-12 18:32:34.09114	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	1	0.5	1
412	57	webauthn	failed	2025-04-12 18:36:01.562651	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	1	0.5	1
413	57	webauthn	failed	2025-04-12 18:36:27.500042	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	1	0.5	1
414	57	password	success	2025-04-12 18:36:58.491662	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
415	57	totp	success	2025-04-12 18:37:08.973582	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
416	57	webauthn	failed	2025-04-12 18:37:13.251272	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	1	0.5	1
417	55	password	success	2025-04-12 18:37:49.586005	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
418	55	totp	failed	2025-04-12 18:37:59.93881	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	2	0.5	1
419	55	totp	success	2025-04-12 18:38:09.909071	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
420	55	webauthn	failed	2025-04-12 18:38:14.177168	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	1	0.5	1
421	55	webauthn	failed	2025-04-12 18:42:16.256199	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	1	0.5	1
422	55	password	success	2025-04-12 18:45:43.074873	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
423	55	totp	success	2025-04-12 18:45:57.049792	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
424	55	webauthn	failed	2025-04-12 18:46:02.245707	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	1	0.5	1
425	55	webauthn	failed	2025-04-12 18:50:46.316391	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	1	0.5	1
426	55	webauthn	failed	2025-04-12 18:55:00.780654	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	1	0.5	1
427	55	webauthn	success	2025-04-12 18:55:51.384297	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
428	22	password	success	2025-04-12 18:57:14.524766	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
429	22	totp	success	2025-04-12 18:57:39.37202	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
430	22	webauthn	success	2025-04-12 18:57:42.787415	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
431	22	password	success	2025-04-12 18:58:37.251387	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
432	22	totp	success	2025-04-12 18:58:52.892597	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
433	22	webauthn	success	2025-04-12 18:59:09.220092	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
434	57	password	success	2025-04-14 08:52:14.786768	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
435	57	totp	success	2025-04-14 08:52:37.234528	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
436	57	webauthn	success	2025-04-14 08:53:25.427657	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
437	22	password	failed	2025-04-14 08:54:48.673227	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	1	0.5	1
438	22	password	success	2025-04-14 08:54:55.149931	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
439	22	totp	success	2025-04-14 08:55:11.366826	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
440	22	webauthn	success	2025-04-14 08:55:17.974475	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
441	57	password	success	2025-04-14 08:58:02.793548	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
442	57	totp	success	2025-04-14 08:58:17.857776	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
443	57	webauthn	success	2025-04-14 08:58:29.292818	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
444	57	totp	success	2025-04-14 09:00:16.268688	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
445	57	webauthn	success	2025-04-14 09:00:31.479572	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
446	22	password	success	2025-04-14 09:03:18.264268	192.168.2.115	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
447	22	totp	success	2025-04-14 09:03:40.247002	192.168.2.115	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
448	57	webauthn	success	2025-04-14 09:07:51.457407	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
449	22	password	success	2025-04-14 09:13:51.704559	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
450	22	totp	success	2025-04-14 09:15:09.704675	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
451	22	webauthn	success	2025-04-14 09:15:14.324504	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
452	22	password	success	2025-04-14 09:56:42.969466	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
453	22	totp	success	2025-04-14 09:56:53.916225	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
454	22	webauthn	success	2025-04-14 09:57:00.051538	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
455	56	password	failed	2025-04-14 10:04:10.800044	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	1	0.5	1
456	56	password	failed	2025-04-14 10:04:14.284274	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	2	0.5	1
457	56	password	failed	2025-04-14 10:04:15.84379	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	3	0.5	1
458	56	password	failed	2025-04-14 10:04:16.91399	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	4	0.5	1
459	56	password	failed	2025-04-14 10:04:18.029936	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	5	0.5	1
461	22	totp	failed	2025-04-14 10:12:38.848926	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	1	0.5	1
464	55	password	failed	2025-04-14 11:25:09.338658	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	1	0.5	1
465	55	password	failed	2025-04-14 11:25:10.31732	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	2	0.5	1
466	55	password	failed	2025-04-14 11:31:36.045738	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	3	0.5	1
467	55	password	failed	2025-04-14 11:31:41.30368	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	4	0.5	1
468	55	password	failed	2025-04-14 11:31:45.577708	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	5	0.5	1
469	54	password	success	2025-04-14 11:32:58.463667	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
470	54	totp	failed	2025-04-14 11:33:07.533155	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	1	0.5	1
471	54	totp	failed	2025-04-14 11:33:09.457394	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	2	0.5	1
472	54	totp	failed	2025-04-14 11:33:10.193899	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	3	0.5	1
473	54	totp	failed	2025-04-14 11:33:11.120522	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	4	0.5	1
474	54	totp	failed	2025-04-14 11:33:12.323257	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	5	0.5	1
475	22	password	success	2025-04-14 11:34:16.453731	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
476	22	totp	success	2025-04-14 11:34:28.600184	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
477	22	webauthn	success	2025-04-14 11:34:32.950069	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
478	57	password	failed	2025-04-14 11:48:01.095827	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	1	0.5	1
479	57	password	failed	2025-04-14 11:48:05.416665	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	2	0.5	1
480	57	password	success	2025-04-14 11:55:33.672463	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
481	57	password	failed	2025-04-14 11:55:49.026779	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	3	0.5	1
482	57	password	failed	2025-04-14 11:55:52.320776	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	4	0.5	1
483	57	password	failed	2025-04-14 11:55:55.449535	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	5	0.5	1
484	22	password	success	2025-04-14 12:00:47.63059	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
485	22	totp	failed	2025-04-14 12:01:06.665409	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	2	0.5	1
486	22	totp	success	2025-04-14 12:01:21.891811	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
487	22	webauthn	success	2025-04-14 12:01:25.508643	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
488	56	password	failed	2025-04-14 12:11:59.508782	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	6	0.5	1
489	22	password	success	2025-04-14 12:19:16.426913	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
490	22	totp	success	2025-04-14 12:24:08.551946	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
491	22	webauthn	success	2025-04-14 12:24:12.567319	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
492	22	password	failed	2025-04-14 14:56:33.226941	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	2	0.5	1
493	22	password	success	2025-04-14 14:56:42.562802	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
494	22	totp	success	2025-04-14 14:57:08.054909	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
495	22	webauthn	success	2025-04-14 14:57:12.644199	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
496	56	password	failed	2025-04-14 15:31:22.375757	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	7	0.5	1
497	54	password	success	2025-04-14 15:33:42.694249	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
498	54	totp	failed	2025-04-14 15:33:59.732382	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	6	0.5	1
499	57	password	success	2025-04-14 16:09:12.801985	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
500	57	totp	success	2025-04-14 16:09:29.586768	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
501	57	password	success	2025-04-14 16:32:40.803458	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
502	57	totp	success	2025-04-14 16:33:27.740565	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
504	57	webauthn	failed	2025-04-14 16:41:34.087001	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	2	0.5	1
505	57	password	success	2025-04-14 16:48:10.242757	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
506	57	totp	success	2025-04-14 16:48:24.170965	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
507	57	webauthn	failed	2025-04-14 16:48:29.503768	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	3	0.5	1
508	57	webauthn	failed	2025-04-14 16:50:17.074884	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	4	0.5	1
509	57	totp	success	2025-04-14 16:53:36.09846	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
510	57	password	success	2025-04-14 17:11:35.353938	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
511	57	totp	success	2025-04-14 17:11:46.822789	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
512	57	webauthn	failed	2025-04-14 17:21:39.474035	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	5	0.5	1
513	22	password	success	2025-04-14 17:27:13.773265	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
514	22	totp	success	2025-04-14 17:27:26.11872	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
515	22	webauthn	failed	2025-04-14 17:27:30.958473	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	1	0.5	1
516	22	webauthn	failed	2025-04-14 17:31:06.858264	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	2	0.5	1
517	22	webauthn	failed	2025-04-14 17:32:36.999959	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	3	0.5	1
518	22	webauthn	failed	2025-04-14 17:38:06.112579	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	4	0.5	1
519	22	password	success	2025-04-14 17:42:29.439537	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
520	22	totp	success	2025-04-14 17:42:42.255071	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
521	22	webauthn	failed	2025-04-14 17:42:45.53308	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	5	0.5	1
522	54	password	success	2025-04-14 17:47:10.473108	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
523	54	totp	success	2025-04-14 17:47:22.861324	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
524	55	password	success	2025-04-14 17:48:21.047847	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
599	56	totp	failed	2025-04-14 21:13:33.784142	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	4	0.5	1
525	55	totp	success	2025-04-14 17:48:37.801507	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
526	55	webauthn	failed	2025-04-14 17:48:42.212855	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	1	0.5	1
527	55	webauthn	failed	2025-04-14 17:55:32.138895	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	2	0.5	1
528	56	password	success	2025-04-14 18:03:43.591464	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
529	56	totp	success	2025-04-14 18:04:07.294218	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
530	56	webauthn	failed	2025-04-14 18:04:11.574423	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	1	0.5	1
531	56	webauthn	failed	2025-04-14 18:09:42.633597	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	2	0.5	1
532	54	password	success	2025-04-14 18:16:11.617522	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
533	54	totp	success	2025-04-14 18:16:24.241345	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
534	54	webauthn	failed	2025-04-14 18:16:28.754825	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	1	0.5	1
535	54	webauthn	failed	2025-04-14 18:18:56.320328	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	2	0.5	1
536	55	password	success	2025-04-14 18:21:55.987747	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
537	55	totp	success	2025-04-14 18:22:07.988399	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
538	55	webauthn	failed	2025-04-14 18:22:11.877886	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	3	0.5	1
539	55	webauthn	failed	2025-04-14 18:27:03.665544	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	4	0.5	1
540	55	webauthn	success	2025-04-14 18:28:08.291627	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
541	22	password	success	2025-04-14 18:32:22.416228	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
542	22	totp	success	2025-04-14 18:32:37.301427	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
543	56	password	success	2025-04-14 18:34:11.240963	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
544	56	totp	success	2025-04-14 18:34:25.641036	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
545	56	webauthn	failed	2025-04-14 18:34:29.484736	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	3	0.5	1
546	56	webauthn	failed	2025-04-14 18:40:39.912483	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	4	0.5	1
547	54	password	success	2025-04-14 18:43:49.625585	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
548	54	totp	success	2025-04-14 18:43:58.854969	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
549	54	webauthn	failed	2025-04-14 18:44:01.725539	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	3	0.5	1
550	54	webauthn	failed	2025-04-14 18:44:58.710808	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	4	0.5	1
551	54	password	success	2025-04-14 18:52:33.310708	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
552	54	totp	success	2025-04-14 18:52:43.297799	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
553	54	webauthn	failed	2025-04-14 18:52:47.649066	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	5	0.5	1
554	56	password	success	2025-04-14 18:57:05.657687	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
555	57	password	success	2025-04-14 18:57:37.235445	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
556	57	totp	success	2025-04-14 18:57:46.64557	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
557	57	webauthn	failed	2025-04-14 18:57:53.647751	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	6	0.5	1
558	55	password	success	2025-04-14 19:01:31.733385	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
559	55	totp	success	2025-04-14 19:01:49.810464	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
560	55	webauthn	failed	2025-04-14 19:01:53.739354	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	5	0.5	1
561	56	password	success	2025-04-14 19:07:02.834033	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
562	56	totp	success	2025-04-14 19:07:15.473885	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
563	56	webauthn	failed	2025-04-14 19:07:18.630314	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	5	0.5	1
564	56	webauthn	failed	2025-04-14 19:11:09.062112	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	6	0.5	1
565	56	webauthn	failed	2025-04-14 19:13:41.529322	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	7	0.5	1
566	56	webauthn	failed	2025-04-14 19:16:01.853154	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	8	0.5	1
567	56	webauthn	failed	2025-04-14 19:16:41.842398	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	9	0.5	1
568	56	webauthn	failed	2025-04-14 19:17:43.163837	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	10	0.5	1
569	56	webauthn	failed	2025-04-14 19:20:49.031259	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	11	0.5	1
570	56	password	success	2025-04-14 19:22:28.038539	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
571	56	totp	success	2025-04-14 19:22:38.710025	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
572	56	webauthn	failed	2025-04-14 19:22:42.029098	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	12	0.5	1
573	56	webauthn	failed	2025-04-14 19:24:56.658383	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	13	0.5	1
574	56	webauthn	failed	2025-04-14 19:27:43.995397	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	14	0.5	1
575	56	webauthn	failed	2025-04-14 19:29:09.054527	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	15	0.5	1
576	56	webauthn	failed	2025-04-14 19:30:42.368245	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	16	0.5	1
577	56	webauthn	failed	2025-04-14 19:36:37.425809	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	17	0.5	1
578	55	password	success	2025-04-14 19:43:59.606633	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
579	55	totp	success	2025-04-14 19:44:17.519914	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
580	55	webauthn	failed	2025-04-14 19:44:21.34856	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	6	0.5	1
581	54	password	success	2025-04-14 19:59:34.112697	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
582	54	totp	success	2025-04-14 19:59:43.820303	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
583	55	password	failed	2025-04-14 20:14:56.630464	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	6	0.5	1
584	54	password	success	2025-04-14 20:15:27.608656	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
585	54	totp	success	2025-04-14 20:16:09.7049	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
586	54	totp	success	2025-04-14 20:19:05.308897	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
587	54	webauthn	failed	2025-04-14 20:23:49.675398	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	6	0.5	1
588	54	password	success	2025-04-14 20:27:56.769801	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
589	54	totp	success	2025-04-14 20:28:19.385612	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
590	22	password	success	2025-04-14 20:45:01.384517	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
591	22	totp	success	2025-04-14 20:45:15.749093	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
592	22	password	success	2025-04-14 20:59:59.065194	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
593	22	totp	success	2025-04-14 21:00:14.584229	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
594	22	totp	success	2025-04-14 21:00:51.343228	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
595	56	password	success	2025-04-14 21:13:17.458914	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
596	56	totp	failed	2025-04-14 21:13:24.780913	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	1	0.5	1
597	56	totp	failed	2025-04-14 21:13:28.995715	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	2	0.5	1
598	56	totp	failed	2025-04-14 21:13:31.401242	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	3	0.5	1
600	56	totp	failed	2025-04-14 21:13:35.789318	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	5	0.5	1
601	56	password	success	2025-04-15 08:31:07.704557	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
602	56	totp	success	2025-04-15 08:31:24.020477	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
603	56	totp	failed	2025-04-15 08:32:34.442783	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	1	0.5	1
604	56	totp	success	2025-04-15 08:32:49.157663	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
605	55	password	success	2025-04-15 08:52:08.451397	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
606	55	totp	success	2025-04-15 08:53:26.064416	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
607	55	totp	failed	2025-04-15 08:54:08.252581	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	1	0.5	1
608	55	totp	success	2025-04-15 08:54:37.439497	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
609	56	password	success	2025-04-15 09:05:57.407579	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
610	56	totp	success	2025-04-15 09:06:08.006224	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
611	56	webauthn	failed	2025-04-15 09:06:12.392892	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	1	0.5	1
612	56	password	success	2025-04-15 09:10:53.446173	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
613	56	totp	failed	2025-04-15 09:11:12.365572	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	2	0.5	1
614	56	totp	success	2025-04-15 09:11:21.187149	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
615	57	password	success	2025-04-15 09:12:35.580096	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
616	57	totp	success	2025-04-15 09:12:44.508002	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
617	54	password	success	2025-04-15 09:27:09.84525	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
618	54	totp	success	2025-04-15 09:27:25.32922	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
619	54	totp	success	2025-04-15 09:28:06.96092	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
620	54	webauthn	failed	2025-04-15 09:28:12.923258	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	1	0.5	1
621	54	webauthn	failed	2025-04-15 09:30:40.043601	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	2	0.5	1
622	54	webauthn	failed	2025-04-15 09:38:05.363309	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	3	0.5	1
623	56	password	success	2025-04-15 09:48:56.875486	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
624	56	totp	success	2025-04-15 09:49:09.777663	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
625	56	webauthn	failed	2025-04-15 09:52:53.564287	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	2	0.5	1
626	56	password	success	2025-04-15 10:07:38.041489	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
627	56	totp	success	2025-04-15 10:08:08.079629	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
628	54	password	success	2025-04-15 10:30:20.611745	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
629	54	totp	success	2025-04-15 10:30:35.038787	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
630	54	webauthn	success	2025-04-15 10:30:43.936458	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
631	56	password	success	2025-04-15 10:42:11.954948	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
632	56	totp	success	2025-04-15 10:42:26.944053	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
633	56	password	success	2025-04-15 10:43:44.491189	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
634	56	totp	success	2025-04-15 10:43:56.50474	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
635	56	password	success	2025-04-15 10:54:27.633578	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
636	56	totp	success	2025-04-15 10:54:41.182904	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
637	56	webauthn	failed	2025-04-15 10:55:39.835601	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	3	0.5	1
638	56	webauthn	failed	2025-04-15 10:58:42.73079	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	4	0.5	1
639	56	webauthn	failed	2025-04-15 11:03:40.497198	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	5	0.5	1
640	57	password	success	2025-04-15 11:04:52.405155	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
641	57	totp	success	2025-04-15 11:05:06.833913	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
642	57	password	success	2025-04-15 11:27:41.839265	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
643	57	totp	success	2025-04-15 11:27:55.057763	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
644	57	password	success	2025-04-15 11:42:46.384001	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
645	57	totp	failed	2025-04-15 11:43:00.566914	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	1	0.5	1
646	57	totp	success	2025-04-15 11:43:08.421768	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
647	57	webauthn	success	2025-04-15 11:44:14.794226	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
648	57	password	success	2025-04-15 11:49:02.602509	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
649	57	totp	success	2025-04-15 11:49:15.202458	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
650	57	webauthn	failed	2025-04-15 11:57:48.172025	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	1	0.5	1
651	57	webauthn	failed	2025-04-15 12:01:03.15385	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	2	0.5	1
652	57	webauthn	failed	2025-04-15 12:03:57.961076	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	3	0.5	1
653	57	password	failed	2025-04-15 12:08:51.435331	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	1	0.5	1
654	57	password	success	2025-04-15 12:08:57.423266	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
655	57	totp	success	2025-04-15 12:09:13.370759	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
656	57	webauthn	failed	2025-04-15 12:09:18.35258	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	4	0.5	1
657	57	webauthn	success	2025-04-15 12:11:03.048539	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
658	57	password	success	2025-04-15 12:24:30.40056	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
659	57	totp	success	2025-04-15 12:24:46.537016	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
660	57	webauthn	success	2025-04-15 12:34:49.938518	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
661	57	password	success	2025-04-15 12:37:42.644595	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
662	57	totp	success	2025-04-15 12:37:55.336369	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
663	57	webauthn	failed	2025-04-15 12:52:13.203649	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	5	0.5	1
664	56	password	success	2025-04-15 12:54:05.902608	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
665	56	totp	success	2025-04-15 12:54:18.120517	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
666	56	webauthn	failed	2025-04-15 12:54:21.636091	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	6	0.5	1
667	57	password	success	2025-04-15 13:10:27.792016	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
668	57	totp	success	2025-04-15 13:10:43.994189	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
669	57	password	success	2025-04-15 13:12:59.881777	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
670	57	totp	success	2025-04-15 13:13:15.653558	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
671	57	webauthn	success	2025-04-15 13:13:20.336238	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
672	57	password	success	2025-04-15 13:16:20.539817	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
673	57	totp	success	2025-04-15 13:16:37.376364	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
674	57	webauthn	success	2025-04-15 13:16:42.447116	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
675	57	password	success	2025-04-15 13:19:50.190807	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
676	57	totp	success	2025-04-15 13:20:05.918101	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
677	57	password	success	2025-04-15 14:36:16.176345	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
678	57	totp	success	2025-04-15 14:36:27.521993	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
679	57	password	success	2025-04-15 14:51:34.922138	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
680	57	totp	success	2025-04-15 14:51:46.107344	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
681	57	password	success	2025-04-15 15:08:47.677664	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
682	57	totp	success	2025-04-15 15:09:07.244996	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
683	57	password	success	2025-04-15 15:16:13.9881	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
684	57	totp	success	2025-04-15 15:16:28.313803	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
685	57	webauthn	success	2025-04-15 15:16:33.932586	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
686	22	password	success	2025-04-15 15:29:25.227852	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
687	22	totp	success	2025-04-15 15:29:42.73813	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
688	22	totp	success	2025-04-15 15:30:17.118586	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
689	22	webauthn	success	2025-04-15 15:30:21.983689	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
690	22	password	success	2025-04-15 15:45:40.590565	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
691	22	totp	success	2025-04-15 15:45:54.158836	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
692	22	webauthn	failed	2025-04-15 15:46:56.222886	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	1	0.5	1
693	22	webauthn	failed	2025-04-15 15:55:09.722433	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	2	0.5	1
694	22	webauthn	failed	2025-04-15 15:59:12.232522	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	3	0.5	1
695	22	password	failed	2025-04-15 16:12:00.316202	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	1	0.5	1
696	57	password	success	2025-04-15 16:12:10.118519	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
697	57	totp	failed	2025-04-15 16:12:30.149321	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	2	0.5	1
698	57	totp	success	2025-04-15 16:12:38.806341	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
699	57	webauthn	failed	2025-04-15 16:12:44.326747	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	6	0.5	1
700	57	webauthn	failed	2025-04-15 16:15:13.280571	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	7	0.5	1
701	57	webauthn	failed	2025-04-15 16:19:11.181147	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	8	0.5	1
702	57	password	success	2025-04-15 16:30:43.547235	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
703	57	totp	success	2025-04-15 16:30:55.358055	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
704	57	webauthn	failed	2025-04-15 16:38:39.932465	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	9	0.5	1
705	57	webauthn	success	2025-04-15 16:45:05.993051	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
706	57	password	success	2025-04-15 16:48:23.059785	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
707	57	totp	success	2025-04-15 16:48:39.637148	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
708	57	webauthn	success	2025-04-15 16:48:48.944808	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
709	57	password	success	2025-04-15 16:57:37.239644	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
710	57	totp	success	2025-04-15 16:57:48.220451	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
711	57	webauthn	failed	2025-04-15 16:59:36.963364	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	10	0.5	1
712	57	webauthn	success	2025-04-15 17:02:01.72829	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
713	57	password	success	2025-04-15 17:05:01.946766	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
714	57	totp	success	2025-04-15 17:05:15.340433	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
715	57	webauthn	success	2025-04-15 17:05:20.413472	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
716	57	webauthn	success	2025-04-15 17:06:17.282493	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
717	57	password	success	2025-04-15 17:10:37.178365	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
718	57	totp	success	2025-04-15 17:10:53.777677	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
719	57	webauthn	success	2025-04-15 17:11:00.598107	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
720	22	password	success	2025-04-15 17:11:59.568026	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
721	22	totp	success	2025-04-15 17:12:16.03501	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
722	22	webauthn	success	2025-04-15 17:12:22.26519	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
723	54	password	success	2025-04-15 17:17:08.810489	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
724	54	totp	success	2025-04-15 17:17:21.473071	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
725	54	webauthn	success	2025-04-15 17:17:27.836226	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
726	54	password	success	2025-04-15 17:18:10.885316	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
727	54	totp	success	2025-04-15 17:18:36.971613	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
728	54	webauthn	success	2025-04-15 17:27:32.554712	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
729	22	password	success	2025-04-15 17:29:39.620351	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
730	22	totp	success	2025-04-15 17:29:53.744953	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
731	22	webauthn	success	2025-04-15 17:29:59.813161	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
732	56	password	success	2025-04-15 17:30:27.650421	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
733	56	totp	success	2025-04-15 17:30:44.651805	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
734	56	password	success	2025-04-15 17:33:11.653925	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
735	56	totp	success	2025-04-15 17:33:25.797991	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
736	54	password	success	2025-04-15 17:33:50.948516	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
737	54	totp	success	2025-04-15 17:34:06.962528	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
738	54	webauthn	success	2025-04-15 17:34:12.366103	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
739	56	password	failed	2025-04-15 17:37:03.220026	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	1	0.5	1
740	56	password	success	2025-04-15 17:37:09.382719	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
741	56	totp	success	2025-04-15 17:37:23.740224	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
742	56	totp	success	2025-04-15 17:39:06.54036	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
743	56	webauthn	success	2025-04-15 17:39:13.110051	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
744	56	password	failed	2025-04-15 17:46:07.419728	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	2	0.5	1
745	56	password	success	2025-04-15 17:46:12.876559	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
746	56	totp	success	2025-04-15 17:46:26.539275	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
747	56	webauthn	success	2025-04-15 17:46:51.738104	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
748	56	password	success	2025-04-15 17:48:40.543923	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
749	56	totp	success	2025-04-15 17:48:51.546817	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
750	56	webauthn	success	2025-04-15 17:48:55.219101	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
751	57	password	success	2025-04-15 17:50:59.391337	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
752	57	totp	failed	2025-04-15 17:51:24.516699	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	3	0.5	1
753	57	totp	failed	2025-04-15 17:51:31.194531	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	4	0.5	1
754	57	totp	failed	2025-04-15 17:51:34.230873	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	5	0.5	1
755	54	password	success	2025-04-15 17:52:15.983882	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
756	54	totp	success	2025-04-15 17:52:28.370645	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
757	54	webauthn	success	2025-04-15 17:53:53.812372	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
758	54	password	success	2025-04-15 18:06:41.218832	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
759	54	totp	success	2025-04-15 18:06:53.561792	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
760	22	password	failed	2025-04-15 18:07:22.436671	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	2	0.5	1
761	22	password	success	2025-04-15 18:07:28.546241	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
762	22	totp	success	2025-04-15 18:07:46.488632	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
763	22	webauthn	success	2025-04-15 18:07:51.717781	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
764	54	password	success	2025-04-15 18:37:46.579168	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
765	54	totp	success	2025-04-15 18:38:08.959126	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
766	54	webauthn	success	2025-04-15 18:38:18.279377	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
767	57	password	failed	2025-04-15 18:38:36.480297	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	2	0.5	1
768	57	password	failed	2025-04-15 18:38:48.296409	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	3	0.5	1
769	57	password	success	2025-04-15 18:38:54.569422	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
770	57	totp	success	2025-04-15 18:39:06.406026	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
771	57	webauthn	success	2025-04-15 18:39:47.537346	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
772	22	password	success	2025-04-15 18:40:04.681966	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
773	22	totp	success	2025-04-15 18:40:23.023861	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
774	22	webauthn	success	2025-04-15 18:40:30.07397	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
775	54	password	success	2025-04-15 18:45:19.162787	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
776	54	totp	success	2025-04-15 18:45:37.976102	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
777	54	webauthn	success	2025-04-15 18:45:43.329563	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
778	54	password	success	2025-04-15 18:45:57.303942	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
779	54	totp	success	2025-04-15 18:46:07.407237	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
780	22	password	success	2025-04-15 19:02:23.290154	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
781	22	totp	success	2025-04-15 19:02:41.539892	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
782	22	webauthn	success	2025-04-15 19:02:46.611826	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
783	54	password	success	2025-04-15 19:08:02.396606	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
784	54	totp	success	2025-04-15 19:08:16.603112	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
785	22	password	success	2025-04-15 19:09:03.708552	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
786	22	totp	success	2025-04-15 19:09:28.738635	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
787	22	webauthn	success	2025-04-15 19:09:35.8724	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
788	57	password	success	2025-04-15 19:10:54.624992	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
789	57	totp	success	2025-04-15 19:11:08.023326	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
790	57	webauthn	success	2025-04-15 19:11:14.345344	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
791	58	password	success	2025-04-15 19:13:41.694587	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
792	58	totp	success	2025-04-15 19:14:13.730763	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
793	58	totp	success	2025-04-15 19:15:21.213706	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
794	58	webauthn	success	2025-04-15 19:15:39.974954	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
795	22	password	success	2025-04-16 08:52:31.743795	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
796	22	totp	success	2025-04-16 08:53:06.901572	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
797	22	webauthn	success	2025-04-16 08:53:53.888332	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
798	22	password	success	2025-04-16 09:02:15.230768	192.168.2.115	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
799	22	totp	failed	2025-04-16 09:02:31.734367	192.168.2.115	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	1	0.5	1
800	22	totp	success	2025-04-16 09:02:43.768505	192.168.2.115	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
801	22	password	success	2025-04-16 09:27:59.474122	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
802	22	totp	success	2025-04-16 09:28:14.650215	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
803	22	webauthn	success	2025-04-16 09:28:20.531918	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
804	57	password	success	2025-04-16 09:35:17.628223	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
805	57	totp	success	2025-04-16 09:35:37.665764	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
806	56	password	success	2025-04-16 09:36:14.991626	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
807	56	totp	success	2025-04-16 09:36:23.77783	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
808	54	password	success	2025-04-16 09:36:56.56002	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
809	54	totp	success	2025-04-16 09:37:10.409588	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
810	58	password	success	2025-04-16 09:37:42.806784	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
811	58	totp	success	2025-04-16 09:37:48.622196	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
812	58	webauthn	success	2025-04-16 09:40:27.057962	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
813	22	password	success	2025-04-16 09:40:55.030739	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
814	22	totp	success	2025-04-16 09:41:10.018611	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
815	22	webauthn	success	2025-04-16 09:41:16.640611	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
816	57	password	success	2025-04-16 09:41:50.57237	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
817	57	totp	failed	2025-04-16 09:42:07.024774	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	1	0.5	1
818	57	totp	success	2025-04-16 09:42:17.848898	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
819	22	password	failed	2025-04-16 09:42:47.806532	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	1	0.5	1
820	22	password	success	2025-04-16 09:42:54.101038	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
821	22	totp	success	2025-04-16 09:43:13.426814	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
823	57	password	success	2025-04-16 09:47:30.364613	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
826	22	totp	failed	2025-04-16 09:48:32.599681	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	2	0.5	1
829	22	password	success	2025-04-16 10:07:51.463655	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
830	22	totp	success	2025-04-16 10:08:07.318649	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
831	22	webauthn	success	2025-04-16 10:08:12.015614	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
832	22	password	success	2025-04-16 10:40:10.214637	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
833	22	totp	success	2025-04-16 10:40:23.410743	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
834	22	webauthn	success	2025-04-16 10:40:28.214919	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
835	22	password	success	2025-04-16 11:03:25.084198	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
836	22	totp	failed	2025-04-16 11:03:31.11754	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	3	0.5	1
837	22	totp	success	2025-04-16 11:03:42.437352	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
838	22	webauthn	success	2025-04-16 11:03:46.666251	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
839	22	password	success	2025-04-16 11:19:18.747502	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
840	22	totp	success	2025-04-16 11:19:28.908633	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
841	22	webauthn	success	2025-04-16 11:19:33.303651	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
842	54	password	success	2025-04-16 11:20:55.063647	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
843	54	totp	success	2025-04-16 11:21:08.002097	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
844	54	webauthn	success	2025-04-16 11:21:12.997028	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
845	22	password	success	2025-04-16 11:35:27.25925	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
846	22	totp	success	2025-04-16 11:35:44.040448	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
847	22	webauthn	success	2025-04-16 11:35:49.185493	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
848	22	password	success	2025-04-16 11:57:32.22612	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
849	22	totp	success	2025-04-16 11:57:39.810167	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
850	22	webauthn	success	2025-04-16 11:57:45.227229	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
851	22	password	success	2025-04-16 14:52:18.812235	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
852	22	totp	success	2025-04-16 14:52:39.488961	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
853	22	webauthn	success	2025-04-16 14:53:17.80879	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
854	54	password	success	2025-04-16 15:36:24.50025	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
855	54	totp	success	2025-04-16 15:36:39.759576	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
856	54	webauthn	success	2025-04-16 15:36:45.117582	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
857	59	password	success	2025-04-16 15:40:33.301981	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
858	59	password	success	2025-04-16 15:46:20.89036	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
859	59	password	success	2025-04-16 15:47:20.873097	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
860	22	password	failed	2025-04-16 15:48:37.406382	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	2	0.5	1
861	22	password	failed	2025-04-16 15:48:43.844161	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	3	0.5	1
862	22	password	success	2025-04-16 15:48:50.633503	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
863	22	totp	success	2025-04-16 15:49:10.052423	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
864	22	webauthn	success	2025-04-16 15:49:14.983998	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
865	59	password	success	2025-04-16 15:50:45.570741	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
866	59	totp	failed	2025-04-16 15:51:30.432431	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	1	0.5	1
867	59	totp	success	2025-04-16 15:51:39.757662	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
870	22	password	success	2025-04-16 15:53:01.848906	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
871	22	totp	success	2025-04-16 15:53:14.098008	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
872	22	webauthn	success	2025-04-16 15:53:18.438199	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
873	22	password	success	2025-04-16 16:58:53.510496	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
874	22	totp	success	2025-04-16 16:59:06.053089	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
875	22	webauthn	success	2025-04-16 16:59:11.357505	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
876	22	password	success	2025-04-16 17:31:54.318898	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
877	22	totp	success	2025-04-16 17:32:13.326415	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
878	22	webauthn	success	2025-04-16 17:32:17.874632	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
879	22	password	success	2025-04-16 18:05:14.372253	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
880	22	totp	success	2025-04-16 18:05:27.834633	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
881	22	webauthn	success	2025-04-16 18:05:32.269285	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
882	22	password	success	2025-04-16 18:23:07.927681	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
883	22	totp	success	2025-04-16 18:23:23.122283	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
884	22	webauthn	success	2025-04-16 18:23:27.818238	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
885	22	password	success	2025-04-16 18:42:06.084136	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
886	22	totp	success	2025-04-16 18:42:18.797123	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
887	22	webauthn	success	2025-04-16 18:42:23.481108	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
888	22	password	success	2025-04-16 19:07:25.117874	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
889	22	totp	success	2025-04-16 19:08:37.263372	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
890	22	webauthn	success	2025-04-16 19:08:41.798255	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
891	22	password	success	2025-04-16 19:32:13.657	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
892	22	totp	success	2025-04-16 19:32:39.4329	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
893	22	webauthn	success	2025-04-16 19:32:44.057914	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
894	22	password	success	2025-04-16 19:48:09.960524	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
895	22	totp	success	2025-04-16 19:48:26.122304	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
896	22	webauthn	success	2025-04-16 19:48:30.402764	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
897	54	password	success	2025-04-17 15:41:42.589008	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
898	54	totp	failed	2025-04-17 15:41:59.902538	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	1	0.5	1
899	54	totp	success	2025-04-17 15:42:09.326508	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
900	54	webauthn	success	2025-04-17 15:43:20.135878	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
901	54	password	success	2025-04-17 15:58:21.470766	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
902	54	totp	success	2025-04-17 15:58:36.774011	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
903	54	webauthn	success	2025-04-17 15:58:50.821496	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
904	60	password	success	2025-04-17 16:00:54.563441	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
905	60	totp	success	2025-04-17 16:01:23.534449	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
906	60	totp	success	2025-04-17 16:03:36.290788	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
907	60	webauthn	success	2025-04-17 16:05:06.941668	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
908	58	password	failed	2025-04-17 16:05:36.825478	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	1	0.5	1
909	58	password	failed	2025-04-17 16:05:39.584626	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	2	0.5	1
919	22	totp	failed	2025-04-17 16:13:35.7544	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	1	0.5	1
921	22	webauthn	success	2025-04-17 16:14:04.735678	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
922	22	password	success	2025-04-17 16:44:27.924176	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
924	22	webauthn	success	2025-04-17 16:44:50.807727	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
927	57	password	failed	2025-04-17 16:46:59.695124	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	3	0.5	1
931	22	password	success	2025-04-17 16:48:00.558092	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
933	22	webauthn	success	2025-04-17 16:48:22.683737	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
934	22	password	success	2025-04-18 14:14:28.385059	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
935	22	totp	success	2025-04-18 14:14:42.532758	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
936	22	webauthn	success	2025-04-18 14:15:14.448448	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
937	22	password	success	2025-04-21 10:08:23.919486	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
938	22	totp	success	2025-04-21 10:08:57.08313	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
939	22	webauthn	success	2025-04-21 10:09:56.385929	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
940	57	password	success	2025-04-21 16:07:59.077434	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
941	57	totp	success	2025-04-21 16:08:18.053806	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
942	57	webauthn	success	2025-04-21 16:08:50.352336	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
943	56	password	failed	2025-04-21 16:23:50.130286	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	1	0.5	1
944	56	password	failed	2025-04-21 16:23:57.005111	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	2	0.5	1
945	56	password	success	2025-04-21 16:24:02.846873	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
946	56	totp	success	2025-04-21 16:24:20.738599	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
947	56	webauthn	success	2025-04-21 16:24:26.406558	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
948	56	password	success	2025-04-21 16:51:09.454908	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
949	56	totp	success	2025-04-21 16:51:25.408369	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
950	56	webauthn	success	2025-04-21 16:51:30.232105	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
951	58	password	success	2025-04-21 17:26:32.330929	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
952	58	totp	failed	2025-04-21 17:26:45.272915	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	1	0.5	1
953	58	totp	failed	2025-04-21 17:26:56.09915	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	2	0.5	1
954	56	password	success	2025-04-21 17:27:17.740047	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
955	56	totp	failed	2025-04-21 17:27:29.509978	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	1	0.5	1
956	56	totp	success	2025-04-21 17:27:43.509409	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
957	56	webauthn	success	2025-04-21 17:27:47.482812	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
958	56	password	success	2025-04-21 17:47:52.213816	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
959	56	totp	success	2025-04-21 17:48:08.120168	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
960	56	webauthn	success	2025-04-21 17:48:12.533889	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
961	56	password	success	2025-04-21 18:14:52.431903	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
962	56	totp	success	2025-04-21 18:15:11.584654	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
963	56	webauthn	success	2025-04-21 18:15:15.23071	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
964	56	password	success	2025-04-21 18:31:23.534891	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
965	56	totp	failed	2025-04-21 18:31:38.605932	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	2	0.5	1
966	56	totp	success	2025-04-21 18:32:08.343529	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
967	56	webauthn	success	2025-04-21 18:32:12.466387	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
968	56	password	success	2025-04-21 18:46:45.504169	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
969	56	totp	success	2025-04-21 18:47:06.473968	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
970	56	webauthn	success	2025-04-21 18:47:09.992679	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
971	56	password	success	2025-04-21 19:06:10.003258	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
972	56	totp	success	2025-04-21 19:06:23.025895	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
973	56	webauthn	success	2025-04-21 19:06:26.657344	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
974	56	totp	failed	2025-04-21 19:13:57.50599	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	3	0.5	1
975	56	totp	success	2025-04-21 19:14:09.022262	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
976	56	webauthn	success	2025-04-21 19:14:12.596716	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
977	56	password	success	2025-04-21 19:20:28.240832	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
978	56	totp	success	2025-04-21 19:20:40.577389	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
979	56	webauthn	success	2025-04-21 19:20:43.333612	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
980	56	totp	success	2025-04-21 19:34:37.51886	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
981	56	webauthn	success	2025-04-21 19:34:40.772891	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
982	56	password	failed	2025-04-21 19:35:58.498695	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	3	0.5	1
983	56	password	success	2025-04-21 19:36:04.414992	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
984	56	totp	success	2025-04-21 19:36:21.338945	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
985	56	webauthn	success	2025-04-21 19:36:24.677762	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
986	56	password	success	2025-04-21 19:59:36.047684	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
987	56	totp	success	2025-04-21 19:59:49.507277	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
988	56	webauthn	success	2025-04-21 19:59:53.623312	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
989	56	password	change	2025-04-21 20:04:22.009596	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
990	56	password	failed	2025-04-21 20:22:06.527613	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	4	0.5	1
991	56	password	success	2025-04-21 20:22:10.703202	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
992	56	totp	success	2025-04-21 20:22:28.981862	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
993	56	webauthn	success	2025-04-21 20:22:32.916822	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
994	56	password	change	2025-04-21 20:24:41.919931	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
995	56	password	change	2025-04-21 20:25:50.747729	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
996	56	password	success	2025-04-21 20:38:51.61791	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
997	56	totp	success	2025-04-21 20:39:10.798074	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
998	56	webauthn	success	2025-04-21 20:39:14.818219	127.0.0.1	Unknown	Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36	0	0.5	1
999	56	totp	reset	2025-04-21 20:42:26.660769	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1000	56	password	failed	2025-04-21 20:44:03.392155	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	5	0.5	1
1001	22	password	success	2025-04-21 20:45:42.106085	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1002	22	totp	success	2025-04-21 20:46:07.193373	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1003	22	webauthn	success	2025-04-21 20:46:12.829917	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1004	60	password	success	2025-04-21 20:48:19.801293	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1005	60	totp	success	2025-04-21 20:48:41.516533	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1006	60	webauthn	success	2025-04-21 20:49:02.204561	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1008	56	totp	success	2025-04-21 20:52:49.995325	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1009	56	webauthn	success	2025-04-21 20:52:53.611023	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1010	56	password	success	2025-04-21 21:27:01.666964	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1011	56	totp	success	2025-04-21 21:27:25.903021	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1012	56	webauthn	success	2025-04-21 21:27:30.106646	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1013	56	webauthn	reset	2025-04-21 21:29:28.81672	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1014	56	password	success	2025-04-21 21:30:35.396395	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1015	56	totp	success	2025-04-21 21:31:09.900456	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1016	56	totp	failed	2025-04-21 21:32:14.20648	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	4	0.5	1
1017	56	totp	success	2025-04-21 21:32:38.266129	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1018	56	webauthn	success	2025-04-21 21:32:53.873357	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1019	54	password	success	2025-04-21 22:14:55.906258	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1020	54	totp	success	2025-04-21 22:15:14.297238	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1021	54	webauthn	success	2025-04-21 22:15:37.177807	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1022	56	password	success	2025-04-21 22:34:21.534179	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1023	56	password	success	2025-04-21 23:14:25.981383	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1024	56	password	failed	2025-04-21 23:15:41.910369	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	6	0.5	1
1025	56	password	success	2025-04-22 09:13:06.499898	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1026	56	password	success	2025-04-22 09:15:31.559744	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1027	56	totp	failed	2025-04-22 09:17:13.135867	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	1	0.5	1
1028	56	totp	success	2025-04-22 09:17:43.274336	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1029	56	webauthn	success	2025-04-22 09:17:59.765589	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1030	56	password	success	2025-04-22 10:11:04.466831	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1031	56	totp	success	2025-04-22 10:11:19.605215	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1032	56	webauthn	success	2025-04-22 10:11:38.948295	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1033	54	password	success	2025-04-22 10:12:31.472758	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1034	54	totp	success	2025-04-22 10:12:49.290851	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1035	54	webauthn	success	2025-04-22 10:13:11.085534	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1036	61	password	success	2025-04-22 10:19:58.828236	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1037	61	totp	success	2025-04-22 10:21:05.978566	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1038	61	password	success	2025-04-22 10:24:13.821281	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1039	61	totp	success	2025-04-22 10:25:17.599798	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1040	61	webauthn	success	2025-04-22 10:25:22.850756	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1041	56	password	success	2025-04-22 10:55:00.869562	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1042	22	password	success	2025-04-22 11:11:10.746101	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1043	22	totp	failed	2025-04-22 11:13:53.720155	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	1	0.5	1
1044	56	password	failed	2025-04-22 16:00:20.193327	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	1	0.5	1
1045	56	password	success	2025-04-22 16:00:26.029025	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1046	56	totp	success	2025-04-22 16:00:41.27222	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1047	56	webauthn	success	2025-04-22 16:00:57.686391	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1048	56	password	success	2025-04-22 16:29:51.49097	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1049	56	totp	success	2025-04-22 16:30:21.761669	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1050	22	password	success	2025-04-22 16:58:08.837819	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1051	22	totp	success	2025-04-22 16:58:26.961332	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1052	56	password	failed	2025-04-23 09:20:37.651581	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	1	0.5	1
1053	56	password	success	2025-04-23 09:20:43.944589	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1054	56	password	failed	2025-04-23 15:18:52.620471	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	2	0.5	1
1055	54	password	success	2025-04-23 15:19:05.980014	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1056	54	totp	success	2025-04-23 15:19:23.10439	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1057	22	password	success	2025-04-23 15:44:33.031405	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1058	22	totp	success	2025-04-23 15:44:56.714402	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1059	22	webauthn	success	2025-04-23 15:45:09.335491	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1060	57	password	success	2025-04-23 15:46:22.643183	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1061	57	totp	failed	2025-04-23 15:46:41.514672	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	1	0.5	1
1062	57	password	success	2025-04-23 15:47:34.219757	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1063	57	totp	success	2025-04-23 15:47:50.056125	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1064	57	password	success	2025-04-23 16:02:30.210009	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1065	57	totp	success	2025-04-23 16:02:48.131032	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1066	22	password	success	2025-04-23 16:24:25.195748	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1067	22	totp	success	2025-04-23 16:24:46.039498	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1068	22	webauthn	success	2025-04-23 16:24:51.609345	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1069	58	password	success	2025-04-23 16:29:28.091945	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1070	58	totp	success	2025-04-23 16:29:44.486846	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1071	58	webauthn	success	2025-04-23 16:30:32.305077	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1072	58	password	success	2025-04-23 16:32:06.374441	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1073	58	totp	success	2025-04-23 16:32:17.759332	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1074	56	password	failed	2025-04-24 09:49:22.071542	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	1	0.5	1
1075	56	password	failed	2025-04-24 09:49:27.218723	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	2	0.5	1
1076	54	password	success	2025-04-24 09:49:59.899549	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1077	54	totp	success	2025-04-24 09:50:20.022718	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1078	54	password	success	2025-04-24 09:55:44.919686	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1079	54	password	failed	2025-04-24 14:44:36.16597	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	1	0.5	1
1080	54	password	success	2025-04-24 14:44:40.778599	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1081	54	totp	success	2025-04-24 14:44:55.025237	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1082	54	webauthn	success	2025-04-24 14:45:02.935156	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1083	54	password	success	2025-04-24 16:30:01.7226	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1084	54	totp	success	2025-04-24 16:30:17.118417	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1085	54	webauthn	success	2025-04-24 16:30:30.550577	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1086	22	password	success	2025-04-24 16:35:35.086189	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1087	22	totp	success	2025-04-24 16:35:57.000053	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1088	22	webauthn	success	2025-04-24 16:36:04.550466	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1089	54	password	success	2025-04-24 18:28:32.471899	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1090	54	totp	success	2025-04-24 18:29:23.198553	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1091	54	webauthn	success	2025-04-24 18:29:30.353695	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1092	54	password	success	2025-04-24 19:28:46.427901	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1093	56	password	success	2025-04-24 19:42:45.863443	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1094	54	password	failed	2025-04-24 19:48:07.722119	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	2	0.5	1
1095	54	password	success	2025-04-24 19:48:14.711245	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1096	54	password	success	2025-04-24 19:52:59.537852	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1097	54	totp	failed	2025-04-24 19:54:12.11439	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	1	0.5	1
1098	54	password	success	2025-04-24 19:55:50.957892	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1099	54	totp	success	2025-04-24 19:56:40.828273	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1100	54	webauthn	success	2025-04-24 19:56:46.906895	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1101	56	password	success	2025-04-24 19:57:22.508261	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1102	56	totp	failed	2025-04-24 19:57:38.767044	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	1	0.5	1
1103	56	password	success	2025-04-24 19:58:54.811519	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1104	56	totp	success	2025-04-24 19:59:25.843725	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1105	56	webauthn	success	2025-04-24 20:00:05.920661	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1106	56	password	success	2025-04-24 20:06:21.120936	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1107	56	totp	success	2025-04-24 20:07:08.798492	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1108	56	webauthn	success	2025-04-24 20:07:21.376842	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1109	56	password	success	2025-04-24 20:09:49.394449	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1110	56	totp	success	2025-04-24 20:10:25.346469	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1111	56	webauthn	success	2025-04-24 20:10:32.518565	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1112	56	password	success	2025-04-24 21:12:49.805614	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1113	56	totp	success	2025-04-24 21:13:25.88874	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1114	56	webauthn	success	2025-04-24 21:13:32.882291	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1115	54	password	success	2025-04-25 09:44:14.826211	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1116	54	totp	success	2025-04-25 09:44:58.508444	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1117	54	webauthn	success	2025-04-25 09:45:03.293265	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1118	54	password	failed	2025-04-25 10:08:35.876953	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	1	0.5	1
1119	54	password	success	2025-04-25 10:08:42.844272	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1120	54	password	failed	2025-04-25 10:18:57.623864	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	2	0.5	1
1121	54	password	success	2025-04-25 10:19:08.048506	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1122	54	password	success	2025-04-25 10:22:40.632774	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
1123	54	totp	success	2025-04-25 10:23:07.130155	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
1124	54	webauthn	success	2025-04-25 10:23:38.281808	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
1125	54	webauthn	reset	2025-04-25 10:24:19.682684	127.0.0.1	Unknown	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0	0	0.5	1
1126	54	password	failed	2025-04-25 10:39:09.208782	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	3	0.5	1
1127	54	password	success	2025-04-25 10:39:18.070037	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1128	54	totp	success	2025-04-25 10:39:38.924977	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1129	54	password	failed	2025-04-25 11:40:10.755292	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	4	0.5	1
1130	54	password	success	2025-04-25 11:40:17.260773	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1131	54	totp	success	2025-04-25 11:40:39.974747	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1132	54	webauthn	success	2025-04-25 11:41:04.28579	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1133	56	password	failed	2025-04-25 15:50:17.711315	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	1	0.5	1
1134	56	password	failed	2025-04-25 15:50:21.889155	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	2	0.5	1
1135	54	password	success	2025-04-25 15:50:46.318455	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1136	54	totp	success	2025-04-25 15:51:06.668466	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1137	54	totp	failed	2025-04-25 15:54:30.31612	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	1	0.5	1
1138	54	totp	success	2025-04-25 15:54:48.931709	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1139	54	password	success	2025-04-25 16:19:52.105232	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1140	54	totp	success	2025-04-25 16:20:13.957979	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1141	54	password	success	2025-04-25 17:21:28.935033	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1142	54	totp	success	2025-04-25 17:21:56.323343	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1143	54	webauthn	success	2025-04-25 17:22:23.662087	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1144	54	password	failed	2025-04-25 17:22:41.377243	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	5	0.5	1
1145	22	password	success	2025-04-25 17:23:17.095128	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1146	22	totp	success	2025-04-25 17:23:44.967929	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1147	22	webauthn	success	2025-04-25 17:24:18.655508	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1148	54	password	success	2025-04-25 17:25:09.966674	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1149	54	totp	success	2025-04-25 17:25:24.527719	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1150	54	password	success	2025-04-25 17:27:35.13674	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1151	54	totp	success	2025-04-25 17:27:49.471088	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1152	54	webauthn	success	2025-04-25 17:28:14.427337	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1153	55	password	success	2025-04-25 17:31:37.048662	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1154	55	totp	failed	2025-04-25 17:31:54.519587	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	1	0.5	1
1155	55	totp	success	2025-04-25 17:32:11.427522	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1156	55	webauthn	success	2025-04-25 17:32:34.278888	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1157	22	password	success	2025-04-25 17:33:12.590288	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1158	22	totp	success	2025-04-25 17:33:43.279636	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1159	22	webauthn	success	2025-04-25 17:33:50.682952	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1160	22	password	success	2025-04-25 20:25:19.053288	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1161	54	password	failed	2025-04-25 20:25:36.563292	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	3	0.5	1
1162	54	password	success	2025-04-25 20:25:42.604126	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1163	54	totp	success	2025-04-25 20:26:11.240468	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1164	54	webauthn	success	2025-04-25 20:26:20.601751	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1165	62	password	success	2025-04-25 20:35:14.576028	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1166	62	totp	success	2025-04-25 20:35:51.597453	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1167	62	webauthn	success	2025-04-25 20:36:09.091593	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1168	54	password	success	2025-04-25 20:42:57.675706	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
1173	54	totp	success	2025-04-25 21:00:48.864554	127.0.0.1	Unknown	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36	0	0.5	1
\.


--
-- Data for Name: user_roles; Type: TABLE DATA; Schema: public; Owner: ztn
--

COPY public.user_roles (id, role_name, permissions, tenant_id) FROM stdin;
1	admin	{"can_delete": true, "can_update": true, "can_assign_roles": true, "can_view_all_transactions": true, "can_verify_transactions": true, "can_suspend_users": true, "can_modify_trust_scores": true, "can_access_reports": true}	1
2	agent	{"can_transact": true, "can_verify_transactions": true, "can_update": false, "can_access_reports": false}	1
3	user	{"can_transact": true, "can_update": true, "can_view_own_transactions": true}	1
6	user	\N	2
7	admin	\N	2
8	user	\N	3
9	admin	\N	3
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: ztn
--

COPY public.users (id, identity_verified, country, trust_score, last_login, created_at, password_hash, is_active, first_name, last_name, email, deletion_requested, otp_secret, otp_email_label, locked_until, reset_token, reset_token_expiry, tenant_id, is_tenant_admin) FROM stdin;
62	f	Rwanda	0.5	2025-04-25 20:34:51.436008	2025-04-25 20:34:51.436008	scrypt:32768:8:1$tncdMkxlZ9nfTxRP$36e4b56a19048ac21d48eb5577ad7aa2efb34cf8c1e602e5a90747256b17ef7e0f46ccf9f10f04942adfdfc3ecb101aa809416edb7758a714cfe0ebb423caeeb	t	Mamure	Malakai	patrickmutabazi104@gmail.com	f	UY5HHZMX6CQES2B7KSEQPOZ5U47FHEBD	patrickmutabazi104@gmail.com	\N	\N	\N	1	\N
56	f	Rwanda	0.5	2025-04-05 12:29:23.53689	2025-04-05 12:29:23.53689	scrypt:32768:8:1$OJWpX7mTpIOWdCl6$a1019c169683c1d9f0ba5a19278750e4220d14a359699c6d5775dd54013ad8002c2c31019a9513d747218b60a5cd7cbdbc8accb0bb7f829b2db47b66e5a66518	t	Gabriel	Darwin	pathos2m@gmail.com	f	3B6VCMQBMF4A6YKNDYGUDYHYQ4ISOQFX	pathos2m@gmail.com	2025-05-12 01:07:58.014087	\N	\N	1	\N
55	f	Rwanda	0.5	2025-04-01 16:44:25.791296	2025-04-01 16:44:25.791296	scrypt:32768:8:1$23CyaMCxLwRHKVhX$928e7592675b4643a1ed52cc7ecab015b6f0087ce916928b4e900b57642f8fbe14b3557caec42dc0ca07b00c514d0c55fe04dfda2d2309d8b7bfc0c596ae8cc3	t	Dary	Betty	darybetty3@gmail.com	f	ZDK6YKHYBYGRBNJ2QF5Q2X57TKM7OZOZ	darybetty3@gmail.com	2025-04-14 11:29:56.770204	\N	\N	1	\N
69	f	Ethiopia	0.5	2025-04-30 18:13:49.270401	2025-04-30 18:13:49.270401	scrypt:32768:8:1$0vyynJ4tBtoZrCAg$17e2cb70332c92b2c91772acf67cdd9649b6f89792c537557f801e6cb7de64927d7e63106c60e32ff73cbab58419a2dbbfdab084f72bb082719037139dcf81e8	f	bztn	Lab	bztn@iplabsec.com	t	QKZYO43VXAJBY3XVVE76ZNRM5NVWYMUR	bztn@iplabsec.com	\N	\N	\N	1	f
57	f	Rwanda	0.5	2025-04-12 14:34:30.028079	2025-04-12 14:34:30.028079	scrypt:32768:8:1$vqoNg3gUQSJsS5CO$cb03ef586728e5d642fbf67ca817c9425a168e0d6a98f2ba7659725ff6ae361eb5132ab9610acd9a3f9cf4df07ff865eb236e1c9033721b6e940e22d956485e7	t	Bio	test	darypathos@gmail.com	f	RSJWAVXN2SGOYWG6E7O6HSIJ5PTPGEXH	darypathos@gmail.com	\N	211d134dd253fa35cb36184d8319ac870dd44c1275b58fc7165c03a5084aa3fb	2025-04-23 08:26:30.657585	1	\N
61	f	Rwanda	0.5	2025-04-22 10:19:10.455566	2025-04-22 10:19:10.455566	scrypt:32768:8:1$HbgtqUdvnHBTPzQk$1c2d8a12770fbc01eb9a1af17161de714f1ba5000abc421245ddb59afaba7e688b85c19d65ac9bdef11a0f12b8d95a47e02f2be9fd503d6afc740382bb75bed2	t	Testing	Malakai	test@ztn.com	f	E7BISJG6DALTHZGLSACASM4LDKLVK6QO	test@ztn.com	\N	\N	\N	1	\N
59	f	Rwanda	0.5	2025-04-16 15:40:08.087573	2025-04-16 15:40:08.087573	scrypt:32768:8:1$KwPbBcflJ0YfjGI2$a23fbdbbd4c98701e9a55a9d5cb9b02cd6e075f3e7698a1903241fbe6d724a9ead7f64931b9e607d7f518eb4fb643b14c78c01ce1b39df564588b3e5c277f25e	t	Register	ZTN	kabarebe@ztn.com	f	3KPSNYHNYVUBH5O7VPNNC3APMTOKHSI2	kabarebe@ztn.com	\N	\N	\N	1	\N
54	f	Rwanda	0.5	2025-04-01 16:19:38.617654	2025-04-01 16:19:38.617654	scrypt:32768:8:1$JXJDW1OZ0UgnhqOb$be354de47000b79bb659c70a15a72b19f8e2cc75d506454306ccb6166e5623569d0907a349d5938a9ad753ed4222c17f93c6fb47c5b9cf90562aa8ce261f4af4	t	Pathos	Mut	pmutaba2@alumni.cmu.edu	f	MN6M7ZXIJEMHU4Y727YVKIQZKE7V4ULD	pmutaba2@alumni.cmu.edu	2025-04-30 07:02:27.564396	7fac2c25753c3a5641c98069fd65fa8a26e35d1e5ba3a97fe1edb77aae67c644	2025-05-02 04:19:17.829561	1	\N
60	f	Rwanda	0.5	2025-04-17 16:00:39.025068	2025-04-17 16:00:39.025068	scrypt:32768:8:1$7tfl1QHkZ4blxPv1$c75404b163c37308244ac6782a5483a135ebbce59ab067651d50f6cdd9fc3f6b0c4443a8f16a476f0383b23ceb32e1c0dc654258e5c25ea4638fdb1b4e3906ae	t	Dary	Betty	darybetty1@gmail.com	f	LN2T5UMIRCI2KSRJLJBJGNUT3RLFR7Y3	darybetty1@gmail.com	\N	\N	\N	1	\N
22	t	Rwanda	0.5	2025-02-24 14:01:31.716187	2025-02-24 14:01:31.716187	scrypt:32768:8:1$TlIe6YcIj5auEJoK$02476cff4a81bf5b3f927f19d02d3279d13df63758a2a455390046e77954eb880de3d42f24175c5fe1a9f06f10b0b8825845010aec0cc6bc233b42d8d36dc6c7	t	Super	Admin	bztniplab@gmail.com	t	X53DKORNHQY76TV7KTVB6JOGRRIQEPIN	bztniplab@gmail.com	2025-04-27 10:39:26.879468	4866df6c0ae9c93aeacd2e0d05c0ff4368a774ad357cca372d1cf9ab3700eacc	2025-04-28 01:48:53.546632	1	\N
58	f	Rwanda	0.5	2025-04-15 19:13:24.519969	2025-04-15 19:13:24.519969	scrypt:32768:8:1$FLczVs7batmQijC1$c46dddc84b7b3dcaee43a2312732c1f590131616cf1fd9a4cc48a6f881fa4b72230018f7c613d2c1170c00ba581ecd61a5de00fc5cf4bd5ea9eb2c925b4236fb	t	Mutabazi	Erinsto	patrick.mutabazi.pj1@naist.ac.jp	f	AMUDAHCNWIPOQIGFTZGNTRSIW64XWH6I	patrick.mutabazi.pj1@naist.ac.jp	2025-04-17 07:20:47.034038	\N	\N	1	\N
70	f	Rwanda	0.5	2025-05-12 17:16:27.819872	2025-05-12 17:16:27.819872	scrypt:32768:8:1$LJTFlRWD9WH6gfC0$e84d370ccdecd1a66c8aebaa55ff86d9656dffa3673ee9c03bc7c5e8193e9a2231af68b664959438aed79584c28cacf7e5f7d43520e4ebba2d160120d6ffc2d9	t	Sensei	Youki	youki@gmail.com	f	WQI2RF2QQYSFKMSLP7D5SCQ7KUUY3EHQ	youki@gmail.com	\N	\N	\N	1	f
\.


--
-- Data for Name: wallets; Type: TABLE DATA; Schema: public; Owner: ztn
--

COPY public.wallets (id, user_id, balance, currency, last_transaction_at) FROM stdin;
42	57	0	RWF	\N
43	58	0	RWF	\N
44	59	0	RWF	\N
45	60	0	RWF	\N
46	61	0	RWF	\N
40	55	13989	RWF	\N
47	62	0	RWF	\N
39	54	41371	RWF	\N
41	56	1830	RWF	\N
48	69	2300	RWF	\N
49	70	0	RWF	\N
\.


--
-- Data for Name: webauthn_credentials; Type: TABLE DATA; Schema: public; Owner: ztn
--

COPY public.webauthn_credentials (id, user_id, credential_id, public_key, sign_count, transports, created_at) FROM stdin;
22	57	\\x284398b98c12f823d682bdadb763846fe239c8617b9d105cd87c76e053c1005a02adb0d73288881c5882499accf9177050916bdc87fd537dc76c71556897200c62fbe11ea8a4e24794a04e2cb1409c5c11b7604171c5a57d1b8fded391f635b0020e905f3f2e6c9575d1bf7657161d4df1e3e0690c21853173a8d37ff4214f895796a6b58e517a56ce88caf4bb28425a3c1f2751e5756d70e241c4effcfba40ab152807bee064619c31ce0711b23105e1d856923ab5b787f7f79f196bf954d7a11aba50842b0ec15642c55a8b55be6adebfc5c6cb9ee9711a248bc4ed35432b5bf3fe04d0e512610d832dcbd788e8cbaa433e2ad3ed9b774407de522dd769e759e6ef02cdd33e50e16375e6d0a365fd7ce6bf83255cf14fbd3bfa08827b18226	\\xa501020326200121582081ab45fc7e3caec18bf48a0f1f51e2e5bb8e3e36dadf7912d7480d0511f81bf9225820fb9f8aa1861794292df553ae1f66d7a88ae1af2d8a063ed5c6050ff84dcf6852	0	nfc,usb	2025-04-23 06:48:06.429431
23	57	\\xf5909bbff8ca1eddac96ee78afc84b308f06f02f	\\xa50102032620012158206d9767d583699bbc00844fc5abe01cd96a1a8a5ad702f3b5b07379d9b3760480225820244462f8d89a17cb891fd4eb44f9460299061b86a53f9882be3e9598ac9a588e	0	hybrid,internal	2025-04-23 06:55:02.984539
24	57	\\xc8361618420e7e503606f8cf3cb72b91	\\xa50102032620012158202c42750d2d1aaf6fb1146bb25df12cba0314b06b2cb929bd11c0315819900e2f225820e6f773966867ab11d4d17c7a5ae51e654ce1d193c9fe641aa756212100683322	0	hybrid,internal	2025-04-23 07:03:11.12136
19	22	\\x1c08e6cf7e1e23f755af7ee59aba44e04dfecc8deaf3bc54e7867711799624efb71702e4620e6abd87e3d50bcdec9fdb4023c6194bbc7a632482b8121ed8a4eb17b8e3f64b1574f70da572b5492b340b175d6c191e0d2b832b7a35c8434901a41cd9f9a5b7b89cccb976311ebf736d4c300f75e59e388a768e19b4bb12706b9bf3836f26cd546a177aa7c1bcc928f0f4500ec2eec28afe0843ae465f221d33fff41f2caa842c1df82b38a90504acff2794d7e778a1366d2be5bc58f4e34550e7f36a79570105e052914644fe01a7200eec3b4b89eaf3caea5f168c4292965df382cab3e1d5843401d9307f157c149a0ba1beb86cd44028f6442bee4837f0d6736bd5fef2f1c08e0eedd1ff365dc2beb70d0f1a147d67e1f9f50a7959b58388db	\\xa5010203262001215820a4ec31e38068ddcdc8051ec95e13e38746a674fe9a68025e006906b00f177f5322582011072cd8af9a1befeee0eb765fb1577e43b7b15d0644dcca8bf91aac61e75f9a	42	nfc,usb	2025-04-22 07:58:44.997085
25	58	\\x328c348c148f41748513f459a21111040f41c9362776cd6d24622aac9df7d64f0be601561bc50ef277630f27ebc14e1fa5a0e468d91335ca60f13e5d285088b8b19cfb123fa42440298ee74a6fe76c7bd3cdf7167984243cef954454bcb555a625f56b9ff4ab33d886e074381a01b4952cec51709c4bf408678de72e2671c3ec4c8045cd3f28b6144765883af0586cd4b2a128c8e552c4ba6b57e308a74a03427ac6f3f4d7dd3ba7e4b537efa840aff23e702507c44dc396720b8552e910287422921ed05ccb26fe7bd4d170774ba08ef6287bde03e7926b51797e449a12f1964b2c441030912aef3b70559e21870b41d439d14b24270934aa70e202db8b8fabd8269e5b41d98fbff15ef0526da4e2057d494537a9eebeb41504f4212e074624f0e708379dfeffc0aafcceecdfd5f581	\\xa50102032620012158202476e8b0ded09eb4609dda68e36b75a091cfe97b76cfbdc1ab6b9fdbe39bdbc8225820e4498ca1fe0a8865d21078e9457c8c42e041b4e29f5f1ee1625d33be271a8257	1	nfc,usb	2025-04-23 07:29:53.10295
30	55	\\xa4c1c7874274b3b45406324af9bf9264ca299d10dab9aaec9150fba8489d736697a9b79d756228fa00b414ec90f89f5532e14a10ea670489b6466cc04c0d2653c302fd6510ab052bcedad88e05a88c97c5e1e890b22de2c9e233b1c798e2850ac99c2c7a75e73ed9b6098692414d6c47199ca578879c1c80ffd7c2912bd9b79102b691dcef321e53701c8d1ba99046cf29ed699f02adb05847905082f1341cb1117c82e29205106b67010306a27b872beedd99cc0c03e625fc1282c79c931d5fb9121cae6370ecec0ca8140d35b44a00b73daabb65edd736e4df1d1e6de15f25faa8bddec424c14f93a4d12925ab4e4d78098e7e04aa1f25bd733777066b2f1a6eb1df26b701b67b6f9249f0dfe6ab3f004b13a9bd82c533bbd1a64ee5f17c4c	\\xa5010203262001215820a786d0d66226922aca4e986e4707e4488e0e3831e3d391d17b6273ab92b00e64225820470b0bf35052ebdb497a57a960c5a443b99342433a9a9e512d75c717f1cda62c	7	nfc,usb	2025-04-25 08:32:23.603825
35	22	\\x64908dc306ababa65dda4eb4933dd786	\\xa50102032620012158209cb4af88167735e319abf3c5f98d7dd890d95847d496e0b0c68b0dc722665b212258203e46100aca5caefd33092d049554c3d507a22e4a5d579cdead2070cb34de2877	3	hybrid,internal	2025-05-03 14:27:14.407725
32	22	\\xa79fb4526d980cb2c0f1622c4df9d4d8e4fd010d	\\xa50102032620012158202ce8592cf67b0a6e5c5f9ec186afe42b996064794347d75ee8a7645dbb0ae75a225820b4d943b81f7764b539713a9cb8b6b18128294d1dc4c1291fcccb630680f85bed	0	hybrid,internal	2025-04-30 07:29:53.472617
33	69	\\x3d2dcd3c6bebe015026816f4b661379640f0bdee	\\xa5010203262001215820eb2c49fa3e853da43397c433a19704acb27f89fdd63d25834023ab5df143f75a2258206e0554a5f6759ee822f99ed58a217bb92a6ee2dfc70521b900f3ae7620e19c15	1	hybrid,internal	2025-04-30 10:15:30.606899
36	70	\\x92fb0dea1ced02c9b52770d9fe5a94b579d189b5163d5e38c07119114cbcec84534e350edf3e95f764cf20e855a573430e91f8452d95a945b3938ac4ca2ca7ea77548dd8e113e7f5f1557c191d37eb87f9c6c6b3aa4f2c8ca5720ebe6da4a9d0ae15a96cc7c13c71bd27dae79de8c9a6f40477ba04a6dcb7ae4bed2144f13a97117404dc6671fd4ff3ece7cba33ed9693c51d7f360d67245f033902009e32692b3a6e8af9455b21073ac3dc7a5369018dae7af2111753d85dbf2a07150f2ee4a040944af51b6009f46e9bdf10d7efee1855c60befbc8f6c64ba354fbedd218d48e1b3c4cc37412c421b2d1ef8ec1d14a96e1a8996e2d2964429935b74633e388f935a8ccfbd23db1292e50ac84f36a99982facfd69704e515a2fbc14242b1fe1	\\xa5010203262001215820a9fd374c979158c865480118e9fbe8c85c89e44ea24b8b6288a6c3a39b9052ae2258203938ad97e68fe47e7a75d63ae95392f59cfe1b2f0b05ef985b52445f7ec1a06b	1	nfc,usb	2025-05-12 08:19:33.475884
29	54	\\x920043250c398225568f7409bea15840bdf9517a1a780017471e932fa81b152a1be28ca2775abac20abd873073d1054f1d42e640b943678926fb1de240b3782f47a11c6ada9c8a7d8d45e47e8b704a1d632ecda6f78cab0ef630cd05c3a194cb21cfc646e3075e488a88220ac4d621089a022e00cd405ba1312f96ea48904610a1ae07a6ec3f7953a706639aa6297c79c4539ff999b157065078062621343f152b00c572bb914044f573dabd894ddcd0bb0972ad351464d89a8e9f7163e983df789411dbf0146116e309d615500b8a5bae138c06377b6e50d9a29365bc8d4812735cd74084646d28c700bfacd10ccd5c8eaabd3551ea430959ea7772336d8dab241f9fee5ab2d717fc577935ee9d922b2ab07c8027291394f4a2b3e3f4141030	\\xa50102032620012158205fb1cadeb20f2b2085be2bb0b21f500728a8137c27e477b9cd494ce14117e99f2258209dbbdc07a843f3ea5fc6d5ffdfa834b02bcd864061ba14e55f0a7431f03eb9a2	52	nfc,usb	2025-04-25 08:28:08.094954
26	56	\\x4ff775f9dd93d9b93ba868008bd67f8da6c22bc977a148372ad1803e409207c82c8eeb1f904df5e07d1bbf08edc066d7b1dd24ab871eb2ffcd2afc7925346e35ebf7a8ce6574344e8242799b98b79f5fa7a812537b0b22c76b2ded77f814a57f89194ad84c76d2c22eebad2d7df6d7868540158f50075d85574cbfdc2fc67e06e5593f2c5c11b778eea0664213d4bfabd9d8b01902c901209e11da0ea7c983b24b3cfc4a3bd871d3483a3a4f0174129af96816f042a1b06452f791fa8fb7ac53057cc53d893f43633cf1283539da5d8a94a71802cf0184004d2912225e9c6c224f1efa9d2edaf04fb0c1c1f94686060dc1ff36129a7b2025ecaaf8ac394183681834c23eb235ba2fe90223d2cbc948ddbc94ab9c7a9bda1bfa0523074c07ca09	\\xa501020326200121582070d453a4ac0d636aa0786c48687d9b6ddf401856be4bcb0c33af6a87f315ad08225820e3401143e4d7dc2a70286865fb8413b24fd45c9e5a000709e7d04ad6a72513f7	12	nfc,usb	2025-04-24 10:59:59.686143
34	69	\\xd76ff19d092ba6cc5ab82564ed1f4500e43ec2a192e63afc694cf5780160d9628f3f416982aeb41882fa2eb0d04dcf08f2240921dffae66bf705e7f14db656cf643ec49c14f905d2930e1451aa3464322d1629e8578e6dcb45f6db920a18035aa7d6ac1432cf26d71fcdc854af6d52c9f51ece99809bfbed9a14661f89ebe10922c70341981e37397b9404cdc1939b581817054d4eb9cb829c777fb7ae69d50475de233dc8fee6447f9a0265e73356270a2f1d5b3ffc7161a29361e4e8b32f02c779673f1317f30c52dde074a85ccda3150c6d66417c6ab9259dd7ef8948c00223b8d217d5602b316720fdf52582246fdea2ae77d3005fe4661de19dc70f8ce0c05cc70f2298aa2f4fb7a5dca06849a136973b6c3c2f2e26e3a914f19fa8e998	\\xa50102032620012158202c1d7202329b00a4fc85a2af92620580d8498f4b80cb4c65fece17fcb976176022582094ae32330cdbdea076ed7ef4c4798dfe364cb7eed802e31c870ef9072824a76f	2	nfc,usb	2025-04-30 10:19:50.866389
31	62	\\xfa5c3cfeefaa6ed48aec7b061e282143c1c50b729b4161be7af8fb197cea3a2f3b34527fd26ff6c4b146781f922fa15d40acd060e24f75ed11e17181da36cb97cd861e6ccc6bc98c05119fdcef74e1e459d368f5a226d101796b86233d82ef408973c9b174f3c684b67d2193b97f5497db5ff605d80c122370364dfa3c51954a1dce6ae3f1b98b35c71840e7bff38e57c291a6e09c0cf3ab46be2b122197ff02684922a779a4a943875a44491230db9a6ff4cec1fa831d1b1c40ee4c84200c9d0112ec834d8b83e9808049b5d380d5a4871a7a7f434c9ba58282965a88af2d3c4dc0a96edfe2ff5dac05b83d39a84ca5ff99aca8134b469114ea2695d1d7188338983aa00e85984df1e0e067f484ecc254d2065f2c026562147554b5d63e426e	\\xa50102032620012158202a3f32c25dd63008e253bf4fc1d5f27acaeb2fd210edf9a95a8aaf392cc9e4a122582019ca3976a72c96448cb50b59ab0dac24adae297d147440e50b7cd558c7cd2b1b	11	nfc,usb	2025-04-25 11:36:01.521725
\.


--
-- Name: headquarters_wallet_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ztn
--

SELECT pg_catalog.setval('public.headquarters_wallet_id_seq', 1, true);


--
-- Name: otp_codes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ztn
--

SELECT pg_catalog.setval('public.otp_codes_id_seq', 76, true);


--
-- Name: password_history_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ztn
--

SELECT pg_catalog.setval('public.password_history_id_seq', 19, true);


--
-- Name: pending_sim_swap_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ztn
--

SELECT pg_catalog.setval('public.pending_sim_swap_id_seq', 19, true);


--
-- Name: pending_transactions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ztn
--

SELECT pg_catalog.setval('public.pending_transactions_id_seq', 1, false);


--
-- Name: real_time_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ztn
--

SELECT pg_catalog.setval('public.real_time_logs_id_seq', 2095, true);


--
-- Name: sim_cards_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ztn
--

SELECT pg_catalog.setval('public.sim_cards_id_seq', 173, true);


--
-- Name: tenant_users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ztn
--

SELECT pg_catalog.setval('public.tenant_users_id_seq', 5, true);


--
-- Name: tenants_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ztn
--

SELECT pg_catalog.setval('public.tenants_id_seq', 1, false);


--
-- Name: transactions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ztn
--

SELECT pg_catalog.setval('public.transactions_id_seq', 216, true);


--
-- Name: user_access_controls_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ztn
--

SELECT pg_catalog.setval('public.user_access_controls_id_seq', 61, true);


--
-- Name: user_auth_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ztn
--

SELECT pg_catalog.setval('public.user_auth_logs_id_seq', 1605, true);


--
-- Name: user_roles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ztn
--

SELECT pg_catalog.setval('public.user_roles_id_seq', 9, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ztn
--

SELECT pg_catalog.setval('public.users_id_seq', 70, true);


--
-- Name: wallets_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ztn
--

SELECT pg_catalog.setval('public.wallets_id_seq', 49, true);


--
-- Name: webauthn_credentials_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ztn
--

SELECT pg_catalog.setval('public.webauthn_credentials_id_seq', 36, true);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: ztn
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: headquarters_wallet headquarters_wallet_pkey; Type: CONSTRAINT; Schema: public; Owner: ztn
--

ALTER TABLE ONLY public.headquarters_wallet
    ADD CONSTRAINT headquarters_wallet_pkey PRIMARY KEY (id);


--
-- Name: otp_codes otp_codes_pkey; Type: CONSTRAINT; Schema: public; Owner: ztn
--

ALTER TABLE ONLY public.otp_codes
    ADD CONSTRAINT otp_codes_pkey PRIMARY KEY (id);


--
-- Name: password_history password_history_pkey; Type: CONSTRAINT; Schema: public; Owner: ztn
--

ALTER TABLE ONLY public.password_history
    ADD CONSTRAINT password_history_pkey PRIMARY KEY (id);


--
-- Name: pending_sim_swap pending_sim_swap_pkey; Type: CONSTRAINT; Schema: public; Owner: ztn
--

ALTER TABLE ONLY public.pending_sim_swap
    ADD CONSTRAINT pending_sim_swap_pkey PRIMARY KEY (id);


--
-- Name: pending_sim_swap pending_sim_swap_token_hash_key; Type: CONSTRAINT; Schema: public; Owner: ztn
--

ALTER TABLE ONLY public.pending_sim_swap
    ADD CONSTRAINT pending_sim_swap_token_hash_key UNIQUE (token_hash);


--
-- Name: pending_transactions pending_transactions_pkey; Type: CONSTRAINT; Schema: public; Owner: ztn
--

ALTER TABLE ONLY public.pending_transactions
    ADD CONSTRAINT pending_transactions_pkey PRIMARY KEY (id);


--
-- Name: real_time_logs real_time_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: ztn
--

ALTER TABLE ONLY public.real_time_logs
    ADD CONSTRAINT real_time_logs_pkey PRIMARY KEY (id);


--
-- Name: sim_cards sim_cards_iccid_key; Type: CONSTRAINT; Schema: public; Owner: ztn
--

ALTER TABLE ONLY public.sim_cards
    ADD CONSTRAINT sim_cards_iccid_key UNIQUE (iccid);


--
-- Name: sim_cards sim_cards_mobile_number_key; Type: CONSTRAINT; Schema: public; Owner: ztn
--

ALTER TABLE ONLY public.sim_cards
    ADD CONSTRAINT sim_cards_mobile_number_key UNIQUE (mobile_number);


--
-- Name: sim_cards sim_cards_pkey; Type: CONSTRAINT; Schema: public; Owner: ztn
--

ALTER TABLE ONLY public.sim_cards
    ADD CONSTRAINT sim_cards_pkey PRIMARY KEY (id);


--
-- Name: tenant_users tenant_users_pkey; Type: CONSTRAINT; Schema: public; Owner: ztn
--

ALTER TABLE ONLY public.tenant_users
    ADD CONSTRAINT tenant_users_pkey PRIMARY KEY (id);


--
-- Name: tenants tenants_api_key_key; Type: CONSTRAINT; Schema: public; Owner: ztn
--

ALTER TABLE ONLY public.tenants
    ADD CONSTRAINT tenants_api_key_key UNIQUE (api_key);


--
-- Name: tenants tenants_pkey; Type: CONSTRAINT; Schema: public; Owner: ztn
--

ALTER TABLE ONLY public.tenants
    ADD CONSTRAINT tenants_pkey PRIMARY KEY (id);


--
-- Name: transactions transactions_pkey; Type: CONSTRAINT; Schema: public; Owner: ztn
--

ALTER TABLE ONLY public.transactions
    ADD CONSTRAINT transactions_pkey PRIMARY KEY (id);


--
-- Name: user_roles uq_role_per_tenant; Type: CONSTRAINT; Schema: public; Owner: ztn
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT uq_role_per_tenant UNIQUE (role_name, tenant_id);


--
-- Name: tenant_users uq_tenant_user_email; Type: CONSTRAINT; Schema: public; Owner: ztn
--

ALTER TABLE ONLY public.tenant_users
    ADD CONSTRAINT uq_tenant_user_email UNIQUE (tenant_id, company_email);


--
-- Name: user_access_controls user_access_controls_pkey; Type: CONSTRAINT; Schema: public; Owner: ztn
--

ALTER TABLE ONLY public.user_access_controls
    ADD CONSTRAINT user_access_controls_pkey PRIMARY KEY (id);


--
-- Name: user_auth_logs user_auth_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: ztn
--

ALTER TABLE ONLY public.user_auth_logs
    ADD CONSTRAINT user_auth_logs_pkey PRIMARY KEY (id);


--
-- Name: user_roles user_roles_pkey; Type: CONSTRAINT; Schema: public; Owner: ztn
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT user_roles_pkey PRIMARY KEY (id);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: ztn
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: ztn
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: wallets wallets_pkey; Type: CONSTRAINT; Schema: public; Owner: ztn
--

ALTER TABLE ONLY public.wallets
    ADD CONSTRAINT wallets_pkey PRIMARY KEY (id);


--
-- Name: wallets wallets_user_id_key; Type: CONSTRAINT; Schema: public; Owner: ztn
--

ALTER TABLE ONLY public.wallets
    ADD CONSTRAINT wallets_user_id_key UNIQUE (user_id);


--
-- Name: webauthn_credentials webauthn_credentials_credential_id_key; Type: CONSTRAINT; Schema: public; Owner: ztn
--

ALTER TABLE ONLY public.webauthn_credentials
    ADD CONSTRAINT webauthn_credentials_credential_id_key UNIQUE (credential_id);


--
-- Name: webauthn_credentials webauthn_credentials_pkey; Type: CONSTRAINT; Schema: public; Owner: ztn
--

ALTER TABLE ONLY public.webauthn_credentials
    ADD CONSTRAINT webauthn_credentials_pkey PRIMARY KEY (id);


--
-- Name: otp_codes fk_otp_codes_tenant_id; Type: FK CONSTRAINT; Schema: public; Owner: ztn
--

ALTER TABLE ONLY public.otp_codes
    ADD CONSTRAINT fk_otp_codes_tenant_id FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: real_time_logs fk_real_time_logs_tenant_id; Type: FK CONSTRAINT; Schema: public; Owner: ztn
--

ALTER TABLE ONLY public.real_time_logs
    ADD CONSTRAINT fk_real_time_logs_tenant_id FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: transactions fk_transactions_tenant_id; Type: FK CONSTRAINT; Schema: public; Owner: ztn
--

ALTER TABLE ONLY public.transactions
    ADD CONSTRAINT fk_transactions_tenant_id FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: user_auth_logs fk_user_auth_logs_tenant_id; Type: FK CONSTRAINT; Schema: public; Owner: ztn
--

ALTER TABLE ONLY public.user_auth_logs
    ADD CONSTRAINT fk_user_auth_logs_tenant_id FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: user_roles fk_user_roles_tenant_id; Type: FK CONSTRAINT; Schema: public; Owner: ztn
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT fk_user_roles_tenant_id FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: users fk_users_tenant_id; Type: FK CONSTRAINT; Schema: public; Owner: ztn
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT fk_users_tenant_id FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: otp_codes otp_codes_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ztn
--

ALTER TABLE ONLY public.otp_codes
    ADD CONSTRAINT otp_codes_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: password_history password_history_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ztn
--

ALTER TABLE ONLY public.password_history
    ADD CONSTRAINT password_history_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: pending_sim_swap pending_sim_swap_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ztn
--

ALTER TABLE ONLY public.pending_sim_swap
    ADD CONSTRAINT pending_sim_swap_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: pending_transactions pending_transactions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ztn
--

ALTER TABLE ONLY public.pending_transactions
    ADD CONSTRAINT pending_transactions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: real_time_logs real_time_logs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ztn
--

ALTER TABLE ONLY public.real_time_logs
    ADD CONSTRAINT real_time_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: sim_cards sim_cards_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ztn
--

ALTER TABLE ONLY public.sim_cards
    ADD CONSTRAINT sim_cards_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: tenant_users tenant_users_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ztn
--

ALTER TABLE ONLY public.tenant_users
    ADD CONSTRAINT tenant_users_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: tenant_users tenant_users_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ztn
--

ALTER TABLE ONLY public.tenant_users
    ADD CONSTRAINT tenant_users_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: transactions transactions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ztn
--

ALTER TABLE ONLY public.transactions
    ADD CONSTRAINT transactions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: user_access_controls user_access_controls_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ztn
--

ALTER TABLE ONLY public.user_access_controls
    ADD CONSTRAINT user_access_controls_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.user_roles(id);


--
-- Name: user_access_controls user_access_controls_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ztn
--

ALTER TABLE ONLY public.user_access_controls
    ADD CONSTRAINT user_access_controls_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: user_auth_logs user_auth_logs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ztn
--

ALTER TABLE ONLY public.user_auth_logs
    ADD CONSTRAINT user_auth_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: wallets wallets_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ztn
--

ALTER TABLE ONLY public.wallets
    ADD CONSTRAINT wallets_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: webauthn_credentials webauthn_credentials_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ztn
--

ALTER TABLE ONLY public.webauthn_credentials
    ADD CONSTRAINT webauthn_credentials_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- PostgreSQL database dump complete
--

