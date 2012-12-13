--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = off;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET escape_string_warning = off;

--
-- Name: loadmonitorv2; Type: DATABASE; Schema: -; Owner: loadmonitorv2
--

CREATE DATABASE loadmonitorv2 WITH TEMPLATE = template0 ENCODING = 'UTF8' LC_COLLATE = 'en_CA.UTF-8' LC_CTYPE = 'en_CA.UTF-8';


ALTER DATABASE loadmonitorv2 OWNER TO loadmonitorv2;

\connect loadmonitorv2

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = off;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET escape_string_warning = off;

SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: log_data; Type: TABLE; Schema: public; Owner: loadmonitorv2; Tablespace: 
--

CREATE TABLE log_data (
    id integer NOT NULL,
    nb_appel_simul integer,
    nb_appel_passes integer
);


ALTER TABLE public.log_data OWNER TO loadmonitorv2;

--
-- Name: log_data_id_seq; Type: SEQUENCE; Schema: public; Owner: loadmonitorv2
--

CREATE SEQUENCE log_data_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.log_data_id_seq OWNER TO loadmonitorv2;

--
-- Name: log_data_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: loadmonitorv2
--

ALTER SEQUENCE log_data_id_seq OWNED BY log_data.id;


--
-- Name: log_info; Type: TABLE; Schema: public; Owner: loadmonitorv2; Tablespace: 
--

CREATE TABLE log_info (
    id integer NOT NULL,
    nom_serveur character varying(64),
    pid_test integer,
    log_id_start integer,
    log_id_end integer
);


ALTER TABLE public.log_info OWNER TO loadmonitorv2;

--
-- Name: log_info_id_seq; Type: SEQUENCE; Schema: public; Owner: loadmonitorv2
--

CREATE SEQUENCE log_info_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.log_info_id_seq OWNER TO loadmonitorv2;

--
-- Name: log_info_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: loadmonitorv2
--

ALTER SEQUENCE log_info_id_seq OWNED BY log_info.id;


--
-- Name: serveur; Type: TABLE; Schema: public; Owner: loadmonitorv2; Tablespace: 
--

CREATE TABLE serveur (
    id integer NOT NULL,
    nom character varying(64),
    ip character varying(15),
    domain character varying(64),
    type integer
);


ALTER TABLE public.serveur OWNER TO loadmonitorv2;

--
-- Name: serveur_id_seq; Type: SEQUENCE; Schema: public; Owner: loadmonitorv2
--

CREATE SEQUENCE serveur_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.serveur_id_seq OWNER TO loadmonitorv2;

--
-- Name: serveur_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: loadmonitorv2
--

ALTER SEQUENCE serveur_id_seq OWNED BY serveur.id;


--
-- Name: serveur_type; Type: TABLE; Schema: public; Owner: loadmonitorv2; Tablespace: 
--

CREATE TABLE serveur_type (
    id integer NOT NULL,
    type character varying(64)
);


ALTER TABLE public.serveur_type OWNER TO loadmonitorv2;

--
-- Name: serveur_type_id_seq; Type: SEQUENCE; Schema: public; Owner: loadmonitorv2
--

CREATE SEQUENCE serveur_type_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.serveur_type_id_seq OWNER TO loadmonitorv2;

--
-- Name: serveur_type_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: loadmonitorv2
--

ALTER SEQUENCE serveur_type_id_seq OWNED BY serveur_type.id;


--
-- Name: services; Type: TABLE; Schema: public; Owner: loadmonitorv2; Tablespace: 
--

CREATE TABLE services (
    id integer NOT NULL,
    service character varying(64),
    uri character varying(64),
    alt character varying(64),
    width integer,
    height integer
);


ALTER TABLE public.services OWNER TO loadmonitorv2;

--
-- Name: services_by_serveur; Type: TABLE; Schema: public; Owner: loadmonitorv2; Tablespace: 
--

CREATE TABLE services_by_serveur (
    id integer NOT NULL,
    id_serveur integer,
    id_service integer
);


ALTER TABLE public.services_by_serveur OWNER TO loadmonitorv2;

--
-- Name: services_by_serveur_id_seq; Type: SEQUENCE; Schema: public; Owner: loadmonitorv2
--

CREATE SEQUENCE services_by_serveur_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.services_by_serveur_id_seq OWNER TO loadmonitorv2;

--
-- Name: services_by_serveur_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: loadmonitorv2
--

ALTER SEQUENCE services_by_serveur_id_seq OWNED BY services_by_serveur.id;


--
-- Name: services_id_seq; Type: SEQUENCE; Schema: public; Owner: loadmonitorv2
--

CREATE SEQUENCE services_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.services_id_seq OWNER TO loadmonitorv2;

--
-- Name: services_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: loadmonitorv2
--

ALTER SEQUENCE services_id_seq OWNED BY services.id;


--
-- Name: watched; Type: TABLE; Schema: public; Owner: loadmonitorv2; Tablespace: 
--

CREATE TABLE watched (
    id integer NOT NULL,
    id_watched integer,
    id_watched_by integer
);


ALTER TABLE public.watched OWNER TO loadmonitorv2;

--
-- Name: watched_id_seq; Type: SEQUENCE; Schema: public; Owner: loadmonitorv2
--

CREATE SEQUENCE watched_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.watched_id_seq OWNER TO loadmonitorv2;

--
-- Name: watched_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: loadmonitorv2
--

ALTER SEQUENCE watched_id_seq OWNED BY watched.id;


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: loadmonitorv2
--

ALTER TABLE ONLY log_data ALTER COLUMN id SET DEFAULT nextval('log_data_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: loadmonitorv2
--

ALTER TABLE ONLY log_info ALTER COLUMN id SET DEFAULT nextval('log_info_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: loadmonitorv2
--

ALTER TABLE ONLY serveur ALTER COLUMN id SET DEFAULT nextval('serveur_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: loadmonitorv2
--

ALTER TABLE ONLY serveur_type ALTER COLUMN id SET DEFAULT nextval('serveur_type_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: loadmonitorv2
--

ALTER TABLE ONLY services ALTER COLUMN id SET DEFAULT nextval('services_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: loadmonitorv2
--

ALTER TABLE ONLY services_by_serveur ALTER COLUMN id SET DEFAULT nextval('services_by_serveur_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: loadmonitorv2
--

ALTER TABLE ONLY watched ALTER COLUMN id SET DEFAULT nextval('watched_id_seq'::regclass);


--
-- Name: public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- PostgreSQL database dump complete
--

